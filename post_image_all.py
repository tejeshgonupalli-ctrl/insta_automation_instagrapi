from instagrapi import Client
from utils.watermark_image import add_watermark_image
import time

ACCOUNTS = [
    "session_account3.json",
    "session_account4.json",
    "session_account5.json"
]

CAPTION = """
🔥 Image Automation

Follow 👉 @mybrand

#automation #instagram #ai
"""

def post_image():
    image = add_watermark_image(
        "posts/img.jpg",
        "posts/img_final.jpg",
        "@mybrand"
    )

    for session in ACCOUNTS:
        cl = Client()
        cl.load_settings(session)
        cl.login_by_sessionid(cl.sessionid)

        time.sleep(2)
        cl.photo_upload(image, CAPTION)
        print(f"✅ Image posted with caption: {session}")

if __name__ == "__main__":
    post_image()
