import cv2

def add_image_watermark(input_path, output_path, username):
    img = cv2.imread(input_path)

    h, w, _ = img.shape
    text = f"@{username}"

    cv2.putText(
        img,
        text,
        (int(w*0.05), int(h*0.95)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        2,
        cv2.LINE_AA
    )

    cv2.imwrite(output_path, img)
