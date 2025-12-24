from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import numpy as np
import os
import random

# ============================
#   FIXED — AUTO TEXT FIT
# ============================
def auto_shrink_font(draw, text, max_width, base_font_size):
    """Shrink font so that watermark never gets cut."""
    font_size = base_font_size

    while font_size > 10:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]

        if text_w <= max_width:
            return font

        font_size -= 2

    return font


# ============================
#       IMAGE WATERMARK
# ============================
def add_image_watermark(input_path, output_path, watermark_text="©descent_rahul_"):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size

    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Auto-adjust font size based on width
    base_font_size = int(width * 0.05)
    font = auto_shrink_font(draw, watermark_text, width * 0.90, base_font_size)

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = width - text_w - 20
    y = height - text_h - 20

    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))

    result = Image.alpha_composite(img, txt_layer)
    result.convert("RGB").save(output_path, "JPEG")



# ============================
#       MOVING VIDEO WM
# ============================
def add_video_watermark(input_path, output_path, watermark_text="©descent_rahul_"):
    video = VideoFileClip(input_path)
    vw, vh = video.size

    # Watermark box
    W = int(vw * 0.45)
    H = int(vh * 0.12)

    wm_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wm_img)

    # Auto big font
    base_font_size = int(W * 0.18)
    font = auto_shrink_font(draw, watermark_text, W * 0.95, base_font_size)

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    tx = (W - tw) // 2
    ty = (H - th) // 2

    draw.text((tx, ty), watermark_text, font=font, fill=(255, 255, 255, 140))

    wm_array = np.array(wm_img)

    # ========= RANDOM MOVEMENT OF WATERMARK =========
    # New random target positions every few seconds
    move_interval = 1.5  # seconds
    random.seed(42)

    positions = []
    t = 0
    while t < video.duration + move_interval:
        x = random.randint(40, max(40, vw - W - 40))
        y = random.randint(40, max(40, vh - H - 40))
        positions.append((t, (x, y)))
        t += move_interval

    # Smooth transition function
    def random_move(t):
        # find two keyframes
        for i in range(len(positions) - 1):
            t1, pos1 = positions[i]
            t2, pos2 = positions[i+1]

            if t1 <= t <= t2:
                # linear interpolation
                alpha = (t - t1) / (t2 - t1)
                x = int(pos1[0] * (1 - alpha) + pos2[0] * alpha)
                y = int(pos1[1] * (1 - alpha) + pos2[1] * alpha)
                return (x, y)

        return positions[-1][1]

    wm_clip = ImageClip(wm_array).set_duration(video.duration).set_pos(random_move)

    final = CompositeVideoClip([video, wm_clip])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
