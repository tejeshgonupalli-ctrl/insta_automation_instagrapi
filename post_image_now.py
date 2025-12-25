from instagrapi import Client
import os

SESSION = "session_account3.json"
IMAGE_PATH = "posts"   # folder

cl = Client()
cl.load_settings(SESSION)

# latest image pick cheyyadam
files = sorted(
    [f for f in os.listdir(IMAGE_PATH) if f.endswith(".jpg")],
    reverse=True
)

latest_image = os.path.join(IMAGE_PATH, files[0])

cl.photo_upload(
    latest_image,
    "🔥 Reposted image\n#repost #viral"
)

print("✅ Image posted successfully")
