from instagrapi import Client

cl = Client()

# Replace with your Instagram credentials
USERNAME = "cutiee23665"
PASSWORD = "insta_auto2"

# Log in and save session
cl.login(USERNAME, PASSWORD)
cl.dump_settings("session_account3.json")
print("✅ Session file created successfully!")
