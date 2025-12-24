from instagrapi import Client

USERNAME = "your_username"
PASSWORD = "your_password"

cl = Client()
cl.login(USERNAME, PASSWORD)
cl.dump_settings("session.json")

print("✅ session.json created successfully")
