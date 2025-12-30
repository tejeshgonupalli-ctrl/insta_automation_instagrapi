import time
import json
from datetime import datetime
from pathlib import Path

from auto_scheduler import post_image, post_reel, post_story

JOBS_FILE = Path("scheduled_jobs.json")

print("⏰ Scheduler Runner started...")
print("📂 Watching:", JOBS_FILE.resolve())


def get_run_time(job):
    """
    Backward compatible scheduler time reader
    Supports both:
    - scheduled_time (new)
    - run_at (old)
    """
    run_at = job.get("scheduled_time") or job.get("run_at")
    if not run_at:
        return None
    return datetime.fromisoformat(run_at)


while True:
    try:
        if not JOBS_FILE.exists():
            time.sleep(5)
            continue

        jobs = json.loads(JOBS_FILE.read_text())
        now = datetime.now()
        changed = False

        for job in jobs:
            # Only pending jobs
            if job.get("status") != "pending":
                continue

            run_at = get_run_time(job)

            if run_at is None:
                job["status"] = "failed"
                job["last_error"] = "Missing scheduled_time / run_at"
                changed = True
                continue

            if now >= run_at:
                print(f"🚀 Running job for @{job['username']}")

                # mark as running first
                job["status"] = "running"
                JOBS_FILE.write_text(json.dumps(jobs, indent=2))

                try:
                    if job["post_type"] == "image":
                        post_image(
                            job["session_file"],
                            job["media_path"],
                            job["username"]
                        )

                    elif job["post_type"] == "reel":
                        post_reel(
                            job["session_file"],
                            job["media_path"],
                            job["username"]
                        )
                        time.sleep(60)  # anti-ban delay

                    elif job["post_type"] == "story":
                        post_story(
                            job["session_file"],
                            job["media_path"],
                            job["username"]
                        )

                    else:
                        raise Exception(f"Unknown post_type: {job['post_type']}")

                    job["status"] = "done"
                    print(f"✅ Done for @{job['username']}")
                    changed = True

                except Exception as e:
                    job["status"] = "failed"
                    job["last_error"] = str(e)
                    print(f"❌ Failed for @{job['username']}: {e}")
                    changed = True

                # Save after each job
                JOBS_FILE.write_text(json.dumps(jobs, indent=2))

        if changed:
            JOBS_FILE.write_text(json.dumps(jobs, indent=2))

    except Exception as e:
        print("❌ Scheduler loop error:", e)

    time.sleep(5)

# # ======================================
# # ADVANCED SCHEDULER (OPTIMIZED & STABLE)
# # ======================================

# import json
# import time
# import uuid
# from datetime import datetime, timezone, timedelta
# from pathlib import Path
# from dateutil import parser as dateparser
# from typing import List, Dict
# from post_uploader import upload_post, _is_video


# JOBS_FILE = Path("scheduled_jobs.json")
# CHECK_INTERVAL = 20
# MAX_RETRIES = 3


# # =================================
# # Load & Save Jobs
# # =================================
# def load_jobs() -> List[Dict]:
#     """
#     Safely load scheduled_jobs.json
#     - If file is corrupted, automatically back it up
#     - Create a new clean scheduled_jobs.json so scheduler never crashes
#     """
#     if not JOBS_FILE.exists():
#         return []

#     try:
#         # normal read
#         return json.loads(JOBS_FILE.read_text(encoding="utf8"))

#     except Exception:
#         # JSON corrupted → auto-fix
#         backup = JOBS_FILE.with_suffix(".corrupted.json")

#         try:
#             JOBS_FILE.rename(backup)
#             print(f"[scheduler] ❌ scheduled_jobs.json corrupted → backup saved as: {backup.name}")
#         except Exception as e:
#             print(f"[scheduler] ❌ backup failed: {e}")

#         # create a new clean JSON file
#         JOBS_FILE.write_text("[]", encoding="utf8")
#         print("[scheduler] ✔ New clean scheduled_jobs.json created (auto-fixed)")

#         return []


# def save_jobs(jobs: List[Dict]):
#     JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf8")


# # =================================
# # Create Job (used by auto_bulk_scheduler)
# # =================================
# def create_job(username: str, media_path: str, scheduled_time: str,
#                caption_path: str = None, caption: str = None, password: str = None):
#     job = {
#         "id": str(uuid.uuid4()),
#         "username": username,
#         "password": password,
#         "media_path": media_path,
#         "caption_path": caption_path,
#         "caption": caption,

#         "scheduled_time": scheduled_time,
#         "type": None,
#         "status": "pending",
#         "retries": 0,
#         "created_at": datetime.now(timezone.utc).isoformat(),
#     }

#     jobs = load_jobs()
#     jobs.append(job)
#     save_jobs(jobs)

#     print("\n========== JOB CREATED ==========")
#     print(json.dumps(job, indent=2))
#     print("=================================\n")

#     return job


# # =================================
# # Update Job / Mark Job
# # =================================
# def mark_job(jobs, job_id, **updates):
#     for job in jobs:
#         if job["id"] == job_id:
#             job.update(updates)
#             return


# # =================================
# # Read Caption (if override)
# # =================================
# def read_caption(job):
#     caption = None

#     # caption from caption_path
#     if job.get("caption_path"):
#         cp = Path(job["caption_path"])
#         if cp.exists():
#             return cp.read_text(encoding="utf8").strip()

#     # caption override direct text
#     if job.get("caption"):
#         return job["caption"]

#     return None


# # =================================
# # Process Single Job
# # =================================
# def process_job(job: Dict):
#     print(f"[scheduler] Processing job {job['id']} for @{job['username']}")

#     media = Path(job["media_path"])

#     # auto-detect type
#     if not job.get("type"):
#         job["type"] = "video" if _is_video(media) else "photo"

#     # caption override
#     caption_text = read_caption(job)
#     post_folder = str(media.parent)

#     # if caption override → replace final_caption.txt
#     if caption_text:
#         (Path(post_folder) / "final_caption.txt").write_text(caption_text, encoding="utf8")

#     # upload
#     return upload_post(
#         username=job["username"],
#         post_folder=post_folder,
#         password=job.get("password")
#     )


# def run_loop():
#     print("\n=====================================")
#     print("           SCHEDULER STARTED")
#     print(" Checking interval:", CHECK_INTERVAL, "sec")
#     print("=====================================\n")

#     while True:
#         try:
#             jobs = load_jobs()
#             now = datetime.now(timezone.utc)
#             changed = False

#             # ⭐ Find first job that needs processing
#             job_to_process = None
#             for job in jobs:
#                 if job.get("status") in ("pending", "failed"):
#                     job_to_process = job
#                     break

#             # ⭐ No pending/failed jobs → sleep
#             if not job_to_process:
#                 time.sleep(CHECK_INTERVAL)
#                 continue

#             job = job_to_process
#             status = job.get("status", "pending")

#             # ⭐ Parse scheduled time
#             scheduled = dateparser.parse(job["scheduled_time"])
#             if scheduled.tzinfo is None:
#                 scheduled = scheduled.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))

#             # ⭐ Check if it's time
#             if now >= scheduled:
#                 retries = job.get("retries", 0)

#                 if retries >= MAX_RETRIES:
#                     print(f"[scheduler] Job {job['id']} exceeded max retries → FAILED")
#                     mark_job(jobs, job["id"], status="failed")
#                     save_jobs(jobs)
#                     time.sleep(CHECK_INTERVAL)
#                     continue

#                 print(f"[scheduler] Running job {job['id']}...")
#                 mark_job(jobs, job["id"], status="running")
#                 save_jobs(jobs)

#                 result = process_job(job)

#                 # ⭐ SUCCESS
#                 if result and result.get("ok"):
#                     print(f"[scheduler] Job {job['id']} SUCCESS.")
#                     mark_job(
#                         jobs, job["id"],
#                         status="done",
#                         completed_at=datetime.now(timezone.utc).isoformat()
#                     )
#                     save_jobs(jobs)
#                     time.sleep(CHECK_INTERVAL)
#                     continue

#                 # ⭐ FAILED
#                 else:
#                     retries += 1
#                     print(f"[scheduler] Job {job['id']} FAILED. Retry {retries}/{MAX_RETRIES}")

#                     mark_job(
#                         jobs, job["id"],
#                         retries=retries,
#                         status="failed",
#                         last_error=str(result)
#                     )
#                     save_jobs(jobs)

#                     # ⭐ DO NOT MOVE TO NEXT JOB
#                     print("[scheduler] Holding scheduler until this failed job is resolved...")
#                     time.sleep(CHECK_INTERVAL)
#                     continue

#             # ⭐ If not yet time, just wait
#             time.sleep(CHECK_INTERVAL)

#         except KeyboardInterrupt:
#             print("[scheduler] STOPPED BY USER.")
#             break

#         except Exception as e:
#             print("[scheduler] ERROR:", e)
#             time.sleep(5)


# if __name__ == "__main__":
#     run_loop()
