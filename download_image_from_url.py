from instagrapi import Client

SESSION = "session_account3.json"
POST_URL = "https://www.instagram.com/p/DSnm06fEnO2/"

cl = Client()
cl.load_settings(SESSION)

media_pk = cl.media_pk_from_url(POST_URL)
media = cl.media_info(media_pk)

# download image
cl.photo_download(media_pk, folder="posts")

print("✅ Image downloaded successfully")
