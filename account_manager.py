# ================================
# FIXED ACCOUNT MANAGER (STABLE)
# ================================

import os
import json
import time
import errno
from pathlib import Path
from instagrapi import Client
from typing import Optional

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

LOCKS_DIR = Path(".login_locks")
LOCKS_DIR.mkdir(exist_ok=True)

# FIXED: SINGLE STABLE DEVICE (very important for session reuse)
STABLE_DEVICE = {
    "manufacturer": "Samsung",
    "model": "SM-G973F",
    "android_version": "29",
    "android_release": "10"
}

def _lock_path(username: str) -> Path:
    return LOCKS_DIR / f"{username}.lock"

def _acquire_lock(username: str, timeout: int = 30) -> bool:
    lock = _lock_path(username)
    start = time.time()
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            if time.time() - start > timeout:
                return False
            time.sleep(0.5)

def _release_lock(username: str):
    try:
        _lock_path(username).unlink()
    except FileNotFoundError:
        pass

def session_file(username: str) -> Path:
    return SESSIONS_DIR / f"{username}.json"

def save_session(cl: Client, username: str):
    data = cl.get_settings()
    path = session_file(username)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"[account_manager] Session saved → {path}")

def load_session(username: str) -> Optional[Client]:
    path = session_file(username)
    if not path.exists():
        return None

    try:
        settings = json.loads(path.read_text(encoding="utf8"))
    except:
        return None

    cl = Client()

    # FIXED: Always set same stable device BEFORE loading settings
    cl.set_device(STABLE_DEVICE)

    cl.set_settings(settings)

    try:
        cl.login(username)   # tries using cookies
        cl.user_info_by_username(username)  # verify
        print(f"[account_manager] Session reused successfully for {username}")
        return cl
    except Exception as e:
        print(f"[account_manager] Session reuse failed: {e}")
        return None

def login_with_password(username: str, password: str, trust_session: bool = True) -> Client:
    """
    FIRST tries session reuse.
    If fails → full login with stable device.
    """
    # try to load session first
    cl = load_session(username)
    if cl:
        return cl

    # locking system
    if not _acquire_lock(username):
        raise RuntimeError("Login lock busy")

    try:
        cl = Client()

        # FIXED: ALWAYS USE SAME DEVICE (no random device)
        cl.set_device(STABLE_DEVICE)

        # Login
        cl.login(username, password)

        # Verify
        cl.user_info_by_username(username)

        # Save session
        if trust_session:
            save_session(cl, username)

        print(f"[account_manager] Password login successful for {username}")
        return cl

    finally:
        _release_lock(username)
