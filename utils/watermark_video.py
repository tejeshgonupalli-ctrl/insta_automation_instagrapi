import cv2
import os

def add_story_watermark(video_path, watermark_text):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ Video not found: {video_path}")

    output_path = video_path.replace(".mp4", "_wm.mp4")

    cap = cv2.VideoCapture(video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(
            frame,
            watermark_text,
            (int(width * 0.05), int(height * 0.95)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        out.write(frame)

    cap.release()
    out.release()

    return output_path
