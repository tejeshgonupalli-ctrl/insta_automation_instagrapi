from instagrapi import Client
from utils.watermark_video import add_watermark_video
import time

ACCOUNTS = [
    "session_account3.json",
    "session_account4.json",
    "session_account5.json"
]
CAPTION = """
🔥 Reel Automation

Follow 👉 @mybrand

#reels #automation #viral
"""

def post_reel():
    video = add_watermark_video(
        "posts/reel.mp4",
        "posts/reel_final.mp4",
        "@mybrand"
    )

    for session in ACCOUNTS:
        cl = Client()
        cl.load_settings(session)
        cl.login_by_sessionid(cl.sessionid)

        time.sleep(3)
        cl.clip_upload(video, CAPTION)
        print(f"✅ Reel posted with caption: {session}")

if __name__ == "__main__":
    post_reel()
