import os
import shutil
from instagrapi import Client

SESSION_FILE = "session_account3.json"
CAROUSEL_URL = "https://www.instagram.com/p/DSDWDYOkkFg/"
CAPTION = "🔁 Reposted Carousel"

DOWNLOAD_DIR = "downloads"
POST_DIR = "posts"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 🔥 CLEAN POSTS FOLDER
if os.path.exists(POST_DIR):
    shutil.rmtree(POST_DIR)
os.makedirs(POST_DIR)

cl = Client()
cl.load_settings(SESSION_FILE)
print("✅ Session loaded")

media_pk = cl.media_pk_from_url(CAROUSEL_URL)
media = cl.media_info(media_pk)

files = []

if media.media_type != 8:
    raise Exception("❌ URL is not a carousel")

for item in media.resources:
    if item.media_type == 1:
        path = cl.photo_download(item.pk, folder=DOWNLOAD_DIR)
    elif item.media_type == 2:
        path = cl.video_download(item.pk, folder=DOWNLOAD_DIR)
    files.append(path)

# move ONLY carousel files
post_files = []
for f in files:
    dest = os.path.join(POST_DIR, os.path.basename(f))
    shutil.move(f, dest)
    post_files.append(dest)

cl.album_upload(post_files, caption=CAPTION)

print("🎉 carousel posted successfully!")
