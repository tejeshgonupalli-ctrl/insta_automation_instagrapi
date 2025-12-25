import cv2

def add_watermark_image(input_img, output_img, username):
    img = cv2.imread(input_img)
    h, w, _ = img.shape

    text = f"@{username}"
    cv2.putText(img, text, (20, h-30),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255,255,255), 2)

    cv2.imwrite(output_img, img)
