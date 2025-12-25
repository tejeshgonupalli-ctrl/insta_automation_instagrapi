from instagrapi import Client

USERNAME = "tanyamittal2026"
PASSWORD = "webdev022025@.com"

cl = Client()
cl.login(USERNAME, PASSWORD)
cl.dump_settings("session.json")

print("✅ session.json created successfully")
