import os
from instagrapi import Client

SESSION_FILE = "session_account3.json"
IMAGE_FOLDER = "posts"

CAPTION = """🔥 Carousel post automated
Swipe 👉
#carousel #automation #instagrapi
"""

# Login with session
cl = Client()
cl.load_settings(SESSION_FILE)
print("✅ Session loaded")

# Collect images
images = [
    os.path.join(IMAGE_FOLDER, f)
    for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith((".jpg", ".png"))
]

if len(images) < 2:
    raise Exception("❌ Carousel needs minimum 2 images")

print("📸 Images:", images)

# Upload carousel
cl.album_upload(
    images,
    caption=CAPTION
)

print("🎉 Carousel posted successfully!")
