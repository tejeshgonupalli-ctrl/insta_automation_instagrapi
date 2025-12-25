import sys
from instagrapi import Client

VIDEO_PATH = sys.argv[1]   # mp4 file path
CAPTION = sys.argv[2] if len(sys.argv) > 2 else "Reposted 🔁"

cl = Client()

# Load session file
cl.load_settings("session_account3.json")

# ✅ No login call needed; session is already loaded

print("✅ Session loaded successfully")

cl.video_upload(
    VIDEO_PATH,
    caption=CAPTION
)

print("🚀 Video posted successfully")
