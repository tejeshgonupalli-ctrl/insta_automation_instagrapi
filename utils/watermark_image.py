from PIL import Image, ImageDraw, ImageFont
import os


def add_watermark_to_image(image_path, watermark_text):
    img = Image.open(image_path).convert("RGBA")

    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # ✅ FIXED PART (textbbox instead of textsize)
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = img.width - text_width - 20
    y = img.height - text_height - 20

    draw.text(
        (x, y),
        watermark_text,
        fill=(255, 255, 255, 180),
        font=font
    )

    watermarked = Image.alpha_composite(img, txt_layer)

    os.makedirs("posts/watermarked", exist_ok=True)
    out_path = f"posts/watermarked/{os.path.basename(image_path)}"

    watermarked.convert("RGB").save(out_path, "JPEG")

    return out_path
