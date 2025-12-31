import re
import requests
from instagrapi import Client
from pathlib import Path


def _get_image_url(obj):
    # Version-safe image URL
    if hasattr(obj, "image_versions2"):
        return obj.image_versions2.candidates[0].url
    if hasattr(obj, "thumbnail_url"):
        return obj.thumbnail_url
    raise Exception("Image URL not found")


def download_media_from_url(insta_url, session_file):
    """
    FINAL, version-safe downloader
    Supports:
    - Reel
    - Image post
    - Carousel (ALL images/videos)

    Returns:
        media_paths (list[str])
        caption (str)
        post_type (str)
    """

    cl = Client()
    cl.load_settings(session_file)

    match = re.search(r"/(reel|p)/([A-Za-z0-9_-]+)/?", insta_url)
    if not match:
        raise ValueError("Invalid Instagram URL")

    shortcode = match.group(2)

    media_pk = cl.media_pk_from_code(shortcode)
    media = cl.media_info(media_pk)

    caption = media.caption_text or ""

    output_dir = Path("posts/uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []

    # ---------------- REEL ----------------
    if media.media_type == 2:
        video_path = output_dir / f"{shortcode}.mp4"
        r = requests.get(media.video_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(video_path, "wb") as f:
            for c in r.iter_content(1024 * 1024):
                if c:
                    f.write(c)

        return [str(video_path)], caption, "reel"

    # ---------------- SINGLE IMAGE ----------------
    if media.media_type == 1:
        img_path = output_dir / f"{shortcode}.jpg"
        r = requests.get(_get_image_url(media), stream=True, timeout=60)
        r.raise_for_status()
        with open(img_path, "wb") as f:
            for c in r.iter_content(1024 * 1024):
                if c:
                    f.write(c)

        return [str(img_path)], caption, "image"

    # ---------------- 🔥 CAROUSEL (IMPORTANT FIX) ----------------
    if media.media_type == 8:
        carousel_items = []

        # ✅ MOST RELIABLE SOURCE
        if hasattr(media, "carousel_media") and media.carousel_media:
            carousel_items = media.carousel_media
        elif hasattr(media, "resources") and media.resources:
            carousel_items = media.resources
        else:
            raise Exception("Carousel items not found")

        for i, item in enumerate(carousel_items):
            # IMAGE
            if item.media_type == 1:
                img_path = output_dir / f"{shortcode}_{i}.jpg"
                r = requests.get(_get_image_url(item), stream=True, timeout=60)
                r.raise_for_status()
                with open(img_path, "wb") as f:
                    for c in r.iter_content(1024 * 1024):
                        if c:
                            f.write(c)
                files.append(str(img_path))

            # VIDEO
            elif item.media_type == 2:
                vid_path = output_dir / f"{shortcode}_{i}.mp4"
                r = requests.get(item.video_url, stream=True, timeout=60)
                r.raise_for_status()
                with open(vid_path, "wb") as f:
                    for c in r.iter_content(1024 * 1024):
                        if c:
                            f.write(c)
                files.append(str(vid_path))

        if len(files) <= 1:
            raise Exception("Carousel detected but only one media downloaded")

        return files, caption, "carousel"

    raise Exception("Unsupported Instagram media type")
