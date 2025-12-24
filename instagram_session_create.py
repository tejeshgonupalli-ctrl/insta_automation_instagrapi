# instagram_session_create.py
from instagrapi import Client

cl = Client()
cl.set_user_agent("Instagram 302.0.0.34.111 Android")

USERNAME = " tanyamittal2026"
PASSWORD = "webdev022025@.com"

cl.login(USERNAME, PASSWORD)
cl.dump_settings("session.json")

print("Session OK")
