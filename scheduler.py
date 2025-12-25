from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from post_now import post_now

scheduler = BlockingScheduler()

scheduler.add_job(
    post_now,
    'date',
    run_date=datetime(2025,12,25,20,0),
    args=[
        "sessions/session_account1.json",
        "reel",
        "posts/reel.mp4",
        "🔥 Scheduled Reel",
        ["#reels", "#viral"]
    ]
)

print("⏰ Scheduler started")
scheduler.start()
