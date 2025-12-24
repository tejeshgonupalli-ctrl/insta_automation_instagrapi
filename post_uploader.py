# ===============================
# FIXED UPLOADER (WORKS WITH NEW SESSION SYSTEM)
# ===============================

import time
import random
from pathlib import Path
from instagrapi.exceptions import ClientLoginRequired
from account_manager import load_session, login_with_password

MAX_UPLOAD_RETRIES = 3

def _is_video(path: Path) -> bool:
    return path.suffix.lower() in [".mp4", ".mov", ".mkv", ".webm"]

def load_caption(post_folder: Path) -> str:
    cap_file = post_folder / "final_caption.txt"
    if cap_file.exists():
        return cap_file.read_text(encoding="utf-8").strip()
    return ""

def find_media_file(post_folder: Path) -> Path:
    for file in post_folder.iterdir():
        if file.suffix.lower() in [".mp4", ".jpg", ".jpeg", ".png"]:
            return file
    raise FileNotFoundError(f"No media found in: {post_folder}")

def get_client(username: str, password: str | None = None):
    cl = load_session(username)
    if cl:
        return cl

    if not password:
        raise RuntimeError("No session found and password not provided.")

    return login_with_password(username, password)

def upload_post(username: str, post_folder: str, password=None):
    post_folder = Path(post_folder)
    media = find_media_file(post_folder)
    caption = load_caption(post_folder)

    cl = get_client(username, password)

    for attempt in range(1, MAX_UPLOAD_RETRIES + 1):
        try:
            if _is_video(media):
                print(f"[Uploader] REEL upload → {media.name} (attempt {attempt})")
                res = cl.video_upload(media.as_posix(), caption)
            else:
                print(f"[Uploader] IMAGE upload → {media.name} (attempt {attempt})")
                res = cl.photo_upload(media.as_posix(), caption)

            print("[Uploader] Upload successful.")
            return {"ok": True, "result": res}

        except ClientLoginRequired:
            print("[Uploader] Session expired → full login")
            cl = login_with_password(username, password)

        except Exception as e:
            wait = 2 ** attempt + random.random()
            print(f"[Uploader] Error: {e}, retry in {wait:.2f}s")
            time.sleep(wait)

    return {"ok": False, "error": "Upload failed after retries"}
