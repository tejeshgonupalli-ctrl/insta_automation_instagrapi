# ==============================================
# AUTO BULK SCHEDULER (FULLY OPTIMIZED VERSION)
# ==============================================

import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path

JOBS_FILE = Path("scheduled_jobs.json")


# ---------------------------------------
# Load existing jobs
# ---------------------------------------
def load_jobs():
    if not JOBS_FILE.exists():
        return []
    try:
        return json.loads(JOBS_FILE.read_text(encoding="utf8"))
    except:
        print("❌ ERROR: scheduled_jobs.json corrupted.")
        return []


# ---------------------------------------
# Save jobs
# ---------------------------------------
def save_jobs(jobs):
    JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf8")


# ---------------------------------------
# Utility: check duplicate job
# ---------------------------------------
def job_exists(jobs, media_path: str):
    for j in jobs:
        if j.get("media_path") == media_path:
            return True
    return False


# ---------------------------------------
# AUTO JOB CREATION FUNCTION
# ---------------------------------------
def auto_create_jobs(
    base_folder,
    username,
    password=None,
    start_time="2025-02-25 10:00",
    gap_minutes=30
):
    base = Path(base_folder)
    if not base.exists():
        print("❌ Base folder not found:", base_folder)
        return

    folders = sorted([f for f in base.iterdir() if f.is_dir()])
    if not folders:
        print("❌ No post folders found.")
        return

    jobs = load_jobs()

    # Validate username
    if not username or len(username) < 2:
        print("❌ Invalid username.")
        return

    # Convert start time to datetime
    try:
        dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except:
        print("❌ Wrong start_time format! Use YYYY-MM-DD HH:MM")
        return

    # If start_time is in past → adjust automatically
    now = datetime.now()
    if dt < now:
        print("⚠ start_time was in past → adjusting to future automatically.")
        dt = now + timedelta(minutes=1)

    print(f"\n🔍 Scanning {len(folders)} folders...")
    print("Auto-creating jobs. Please wait...\n")

    created = 0
    skipped = 0

    for folder in folders:
        media = None

        # detect one media file
        for file in folder.iterdir():
            if file.suffix.lower() in [".mp4", ".jpg", ".jpeg", ".png"]:
                media = str(file)
                break

        if not media:
            print(f"⚠ SKIPPED: No media found → {folder.name}")
            skipped += 1
            continue

        # Skip if already exists
        if job_exists(jobs, media):
            print(f"⚠ SKIPPED: Job already exists → {folder.name}")
            skipped += 1
            continue

        # caption detect
        caption_file = folder / "final_caption.txt"
        caption_path = str(caption_file) if caption_file.exists() else None

        # Create job
        job = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password": password,
            "media_path": media,
            "caption_path": caption_path,
            "caption": None,  # keep override empty

            "scheduled_time": dt.strftime("%Y-%m-%d %H:%M"),
            "status": "pending",
            "retries": 0,
            "type": None,
            "created_at": datetime.now().isoformat(),
        }

        jobs.append(job)
        created += 1

        print(f"✔ Job added: {folder.name} → {job['scheduled_time']}")

        # move to next time slot
        dt += timedelta(minutes=gap_minutes)

    save_jobs(jobs)

    # Final summary
    print("\n=====================================")
    print("           BULK JOB SUMMARY")
    print("=====================================")
    print(f"📌 Total folders scanned: {len(folders)}")
    print(f"📌 Jobs created: {created}")
    print(f"📌 Skipped folders: {skipped}")

    if created > 0:
        print(f"⏱ First post:  {jobs[-created]['scheduled_time']}")
        print(f"⏱ Last post:   {dt.strftime('%Y-%m-%d %H:%M')}")
    print("=====================================\n")


# ---------------------------------------
# MAIN TRIGGER
# ---------------------------------------
if __name__ == "__main__":
    auto_create_jobs(
        base_folder=r"C:\Users\w10\Desktop\WebScrapping\final_ready_to_post",
        username="descent_rahul_",
        password="Rahul@12345",   # keep if session fails safe
        start_time="2025-12-04 10:00",
        gap_minutes=30
    )
