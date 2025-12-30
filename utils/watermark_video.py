import os
import subprocess
import uuid

def add_story_watermark(video_path, watermark_text="@yourname"):
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    output_path = video_path.replace(".mp4", "_wm.mp4")
    ass_path = f"temp_{uuid.uuid4().hex}.ass"

    ass_content = f"""
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV

; 🔹 Moving watermark (slow, visible, not disturbing)
Style: MOVE,Arial,48,&H55FFFFFF,&H80000000,&H00000000,0,0,1,2,1,5,20,20,60

; 🔹 Static centre watermark (anti-theft, high transparency)
Style: STATIC,Arial,64,&H25FFFFFF,&H80000000,&H00000000,0,0,1,1,0,5,20,20,20

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

; 🔁 Moving watermark – slow rotation (12 seconds per round)
Dialogue: 0,0:00:00.00,9:59:59.00,MOVE,,0,0,0,,{{\\pos(540,1750)\\frz0\\t(0,12000,\\frz360)}}{watermark_text}

; 🔒 Static centre watermark – anti-theft
Dialogue: 1,0:00:00.00,9:59:59.00,STATIC,,0,0,0,,{{\\pos(540,960)}}{watermark_text}
"""

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    subprocess.run(cmd, check=True)
    os.remove(ass_path)
    return output_path
