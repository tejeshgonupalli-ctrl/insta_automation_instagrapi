import cv2

def add_watermark(input_video, output_video, username):
    cap = cv2.VideoCapture(input_video)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        text = f"@{username}"

        x = int(width * 0.05)
        y = int(height * 0.95)

        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        out.write(frame)

    cap.release()
    out.release()

