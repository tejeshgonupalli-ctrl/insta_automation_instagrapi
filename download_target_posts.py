from instagrapi import Client
from pathlib import Path

USERNAME = "your_username"
TARGET_USER = "target_user"

DOWNLOAD_DIR = Path("downloaded_posts")
DOWNLOAD_DIR.mkdir(exist_ok=True)

cl = Client()
cl.load_settings("session.json")
cl.login(USERNAME, relogin=False)

target_id = cl.user_id_from_username(TARGET_USER)
posts = cl.user_medias(target_id, amount=10)

for media in posts:
    cl.photo_download(media.pk, folder=DOWNLOAD_DIR)

print("✅ Target user posts downloaded")
