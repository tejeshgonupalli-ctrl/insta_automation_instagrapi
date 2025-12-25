from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from instagrapi import Client

cl = Client()
cl.load_settings("session_account3.json")
print("✅ Session loaded")

scheduler = BlockingScheduler()
# -------- POST FUNCTIONS -------- #

def post_image(path, caption):
    cl.photo_upload(path, caption)
    print("✅ Image posted")

def post_reel(path, caption):
    cl.clip_upload(path, caption)
    print("✅ Reel posted")

def post_story(path):
    if path.lower().endswith((".jpg", ".jpeg", ".png")):
        cl.photo_upload_to_story(path)
        print("✅ Image story posted")
    else:
        cl.video_upload_to_story(path)
        print("✅ Video story posted")


    
    
def post_image(path, caption):
    cl.photo_upload(path, caption)
    print("✅ Image posted")

# -------- SCHEDULE JOBS -------- #

from datetime import datetime


# 5:40 PM
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 25, 17, 40),
    args=["posts/img1.jpg", "🔥 5PM Image Post"]
)

# 6:30 PM
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 25, 18, 30),
    args=["posts/reel1.mp4", "🚀 6:30 PM reel"]
)


# 8:00 PM
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 25, 20, 17),
    args=["posts/story.mp4"]
)

# 9:00 PM
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 25, 20, 30),
    args=["posts/img2.jpg", "🌙 9PM post"]
)



print("⏰ Scheduler started...")
scheduler.start()
