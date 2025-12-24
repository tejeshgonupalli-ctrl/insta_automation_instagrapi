from instagrapi import Client

USERNAME = "your_username"

cl = Client()
cl.load_settings("session.json")
cl.login(USERNAME, relogin=False)

# now safe to use
cl.photo_upload("media/photo.jpg", "Hello Instagram 🚀")
