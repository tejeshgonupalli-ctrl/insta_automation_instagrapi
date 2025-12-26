from instagrapi import Client

ACCOUNTS = [
    "session_account3.json",
    "session_account4.json",
    "session_account5.json"
]

def post_story():
    for session in ACCOUNTS:
        cl = Client()
        cl.load_settings(session)
        cl.login_by_sessionid(cl.sessionid)

        cl.photo_upload_to_story("posts/story.jpg")
        print(f"✅ Story posted: {session}")

if __name__ == "__main__":
    post_story()
