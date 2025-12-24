from instagrapi import Client

SESSIONID = "your_instagram_sessionid"

cl = Client()
cl.login_by_sessionid(SESSIONID)

cl.dump_settings("session.json")

print("✅ Logged in using sessionid & session.json saved")
