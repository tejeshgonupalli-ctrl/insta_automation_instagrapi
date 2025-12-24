# fetch_medias.py
import sys, time
from instagrapi import Client

TARGET = sys.argv[1]

cl = Client()
cl.load_settings("session.json")
cl.login(None, None)

uid = cl.user_id_from_username(TARGET)

medias = cl.user_medias_v1(uid, amount=3)

for m in medias:
    if m.media_type == 1:
        cl.photo_download(m.pk)
        time.sleep(6)

print("Done")
