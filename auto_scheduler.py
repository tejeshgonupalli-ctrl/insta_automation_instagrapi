from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from instagrapi import Client
from utils.watermark_image import add_watermark_to_image
from utils.watermark_video import add_story_watermark

from caption_hashtag import generate_caption_and_hashtags



scheduler = BlockingScheduler()


def get_client(session_file):
    cl = Client()
    cl.load_settings(session_file)

    try:
        cl.get_timeline_feed()
    except:
        raise Exception(f"❌ Session expired: {session_file}")

    return cl


# -------- IMAGE POST --------
def post_image(session_file, image_path):
    cl = get_client(session_file)
    username = cl.account_info().username

    original_text = "This post shows an amazing moment captured on camera."

    caption_text, hashtags = generate_caption_and_hashtags(username, original_text)

    caption = f"""{caption_text}

{hashtags}
"""

    watermarked = add_watermark_to_image(image_path, f"@{username}")
    cl.photo_upload(watermarked, caption)

    print("✅ Image posted WITH caption & hashtags")



# -------- REEL POST --------
def post_reel(session_file, video_path):
    cl = get_client(session_file)
    username = cl.account_info().username

    original_text = """
    This reel shows a creative and inspiring video clip.
    """

    caption_text, hashtags = generate_caption_and_hashtags(username, original_text)

    caption = f"""{caption_text}

{hashtags}
"""

    wm_video = add_story_watermark(
        video_path,
        f"@{username}"
    )

    cl.clip_upload(wm_video, caption)

    print("✅ Reel posted WITH GPT caption & hashtags")


# -------- STORY POST --------

from utils.watermark_video import add_story_watermark

def post_story(session_file, path):
    cl = get_client(session_file)
    username = cl.account_info().username

    if path.lower().endswith((".jpg", ".png")):
        wm_img = add_watermark_to_image(path, f"@{username}")
        cl.photo_upload_to_story(wm_img)
    else:
        wm_video = add_story_watermark(path, f"@{username}")
        cl.video_upload_to_story(wm_video)

    print("✅ Story posted WITH SOUND + watermark")



# -------- SAME TIME → DIFFERENT ACCOUNTS -------- #

# 11:25 PM – Account 3
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 27, 18, 10),
    args=["session_account3.json", "posts/img2.jpg"]

)

# 11:25 PM – Account 4
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 27, 18, 11 ),
    args=["session_account4.json", "posts/img2.jpg"]

)

# 11:25 PM – Account 4
scheduler.add_job(
    post_image,
    'date',
    run_date=datetime(2025, 12, 27, 18, 12),
    args=["session_account5.json", "posts/img2.jpg"]

)

# 12:00 PM – Reel (Account 3)
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 27, 18, 40),
    args=["session_account3.json", "posts/reel2.mp4"]

)

# 12:00 PM – Reel (Account 4)
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 27, 18, 41),
    args=["session_account4.json", "posts/reel2.mp4"]

)

# 12:00 PM – Reel (Account 4)
scheduler.add_job(
    post_reel,
    'date',
    run_date=datetime(2025, 12, 27, 18, 42),
    args=["session_account5.json", "posts/reel2.mp4"]

)

# 12:10 PM – Story (Account 3)
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 27, 19, 10),
    args=["session_account3.json", "posts/story.mp4"]
)

# 12:10 PM – Story (Account 4)
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 27, 19, 11),
    args=["session_account4.json", "posts/story.mp4"]
)

# 12:10 PM – Story (Account 4)
scheduler.add_job(
    post_story,
    'date',
    run_date=datetime(2025, 12, 27,19, 12),
    args=["session_account5.json", "posts/story.mp4"]
)

print("⏰ Scheduler started...")
scheduler.start()
