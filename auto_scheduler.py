from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from instagrapi import Client

scheduler = BlockingScheduler()

def get_client(session_file):
    cl = Client()
    cl.load_settings(session_file)

    try:
        cl.get_timeline_feed()   # 🔥 SESSION REFRESH
    except:
        raise Exception(f"❌ Session expired: {session_file}")

    return cl


# -------- POST FUNCTIONS (PER ACCOUNT) -------- #


def post_image(session_file, path, caption):
    cl = get_client(session_file)
    cl.photo_upload(path, caption)
    print(f"✅ Image posted from {session_file}")

def post_reel(session_file, path, caption):
    cl = get_client(session_file)
    cl.clip_upload(path, caption)
    print(f"✅ Reel posted from {session_file}")

def post_story(session_file, path):
    cl = get_client(session_file)

    if path.lower().endswith((".jpg", ".jpeg", ".png")):
        cl.photo_upload_to_story(path)
    else:
        cl.video_upload_to_story(path)

    print(f"✅ Story posted from {session_file}")


# -------- SAME TIME → DIFFERENT ACCOUNTS -------- #

# 11:25 PM – Account 3
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 26, 12, 11),
    args=["session_account3.json", "posts/img1.jpg", "🔥 Account 3 post"]
)

# 11:25 PM – Account 4
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 26, 12, 12),
    args=["session_account4.json", "posts/img1.jpg", "🔥 Account 4 post"]
)

# 12:00 PM – Reel (Account 3)
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 26, 12, 15),
    args=["session_account3.json", "posts/reel1.mp4", "🚀 Reel"]
)

# 12:00 PM – Reel (Account 4)
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 26, 12, 16),
    args=["session_account4.json", "posts/reel1.mp4", "🚀 Reel"]
)

# 12:10 PM – Story (Account 3)
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 26, 12, 20),
    args=["session_account3.json", "posts/story.mp4"]
)

# 12:10 PM – Story (Account 4)
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 26, 12, 21),
    args=["session_account4.json", "posts/story.mp4"]
)

print("⏰ Scheduler started...")
scheduler.start()
