from instagrapi import Client

cl = Client()

# Replace with your Instagram credentials
USERNAME = "tanyamittal2026"
PASSWORD = "webdev022025@.com"

# Log in and save session
cl.login(USERNAME, PASSWORD)
cl.dump_settings("session_account3.json")
print("✅ Session file created successfully!")
