import os
import subprocess
import uuid

def add_story_watermark(video_path, watermark_text="@john.deere143", logo_path=None):
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    output_path = video_path.replace(".mp4", "_wm.mp4")
    ass_path = f"temp_{uuid.uuid4().hex}.ass"

    # ASS subtitle: bottom-center + continuous rotation
    ass_content = f"""
[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: WM,Arial,36,&H70FFFFFF,&H80000000,&H00000000,0,0,1,2,1,5,20,20,60

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,9:59:59.00,WM,,0,0,0,,{{\\pos(360,1150)\\frz0\\t(0,3000,\\frz360)}}{watermark_text}
"""

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    # Build filter
    if logo_path and os.path.exists(logo_path):
        # Overlay logo at bottom-center + spinning text
        filter_complex = (
            f"[1:v]scale=80:80,format=rgba[logo];"
            f"[0:v][logo]overlay=(W-w)/2:(H-h)/2:format=auto[v];"
            f"[v]ass={ass_path}"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", logo_path,
            "-filter_complex", filter_complex,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
    else:
        # Only spinning text
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
