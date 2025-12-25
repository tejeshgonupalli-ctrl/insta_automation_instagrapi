from instagrapi import Client

SESSION_FILE = "session_account3.json"
REEL_PATH = "posts/reel.mp4"

CAPTION = """🔥 Reposted Reel
Follow for more
#reels #viral #trending
"""

cl = Client()
cl.load_settings(SESSION_FILE)

cl.clip_upload(REEL_PATH, CAPTION)

print("✅ Reel posted successfully")
