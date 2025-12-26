import cv2

def add_video_watermark(input_video, output_video, username):
    cap = cv2.VideoCapture(input_video)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(
            frame,
            f"@{username}",
            (int(w*0.05), int(h*0.95)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2,
            cv2.LINE_AA
        )

        out.write(frame)

    cap.release()
    out.release()

