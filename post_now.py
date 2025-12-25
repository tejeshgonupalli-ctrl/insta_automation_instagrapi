from instagrapi import Client
from caption_utils import generate_caption

def post_now(session, post_type, media, caption, hashtags):
    cl = Client()
    cl.load_settings(session)

    final_caption = generate_caption(caption, hashtags)

    if post_type == "image":
        cl.photo_upload(media, final_caption)

    elif post_type == "video":
        cl.video_upload(media, final_caption)

    elif post_type == "reel":
        cl.clip_upload(media, final_caption)

    elif post_type == "carousel":
        cl.album_upload(media, final_caption)

    print("✅ Posted successfully")
