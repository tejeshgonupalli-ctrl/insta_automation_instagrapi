import sys
from instagrapi import Client

# Command line nundi video path
VIDEO_PATH = sys.argv[1]

cl = Client()

# Session load (already login ayina account)
cl.load_settings("session_account3.json")

print("✅ Session loaded")

# 📸 Story upload (video)
cl.video_upload_to_story(VIDEO_PATH)

print("📸 Story uploaded successfully")

