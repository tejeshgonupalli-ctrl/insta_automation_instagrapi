
# THIRD RUN AUTOMATION SCRIPT

import os
from watermark_util import add_image_watermark, add_video_watermark

FILTERED_MAIN_FOLDER = r"C:\Users\w10\Desktop\WebScrapping\filtered_downloads"
OUTPUT_MAIN_FOLDER = FILTERED_MAIN_FOLDER + "_watermarked"

os.makedirs(OUTPUT_MAIN_FOLDER, exist_ok=True)

print("\nStarting Watermarking Process...\n")

for sub_folder in os.listdir(FILTERED_MAIN_FOLDER):

    source_path = os.path.join(FILTERED_MAIN_FOLDER, sub_folder)
    if not os.path.isdir(source_path):
        continue

    output_subfolder = os.path.join(OUTPUT_MAIN_FOLDER, sub_folder)
    os.makedirs(output_subfolder, exist_ok=True)

    print(f"\n📂 Processing Folder: {sub_folder}")

    for file_name in os.listdir(source_path):

        input_file = os.path.join(source_path, file_name)

        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"   🖼 Watermarking IMAGE: {file_name}")
            output_file = os.path.join(output_subfolder, file_name)
            add_image_watermark(input_file, output_file, watermark_text="©descent_rahul_")

        elif file_name.lower().endswith(".mp4"):
            print(f"   🎥 Watermarking VIDEO: {file_name}")
            output_file = os.path.join(output_subfolder, file_name.replace(".mp4", "_wm.mp4"))
            add_video_watermark(input_file, output_file, watermark_text="©descent_rahul_")

        elif file_name.lower().endswith(".txt"):
            out = os.path.join(output_subfolder, file_name)
            with open(input_file, "r", encoding="utf-8") as f:
                data = f.read()
            with open(out, "w", encoding="utf-8") as f:
                f.write(data)

print("\n✔ ALL DONE! Watermarked files saved here:")
print(OUTPUT_MAIN_FOLDER)
