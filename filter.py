
# SECOND RUN AUTOMATION SCRIPT

import os
import json
import shutil
import lzma  # For .xz files

# ====== Settings ======
base_folder = r"C:\Users\w10\Desktop\WebScrapping\insta_downloads"

# Automatically detect the username folder inside insta_downloads
subfolders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

if not subfolders:
    print("No user folder found inside insta_downloads!")
    exit()

# Take the first folder (instaloader always creates only one per run)
source_folder = os.path.join(base_folder, subfolders[0])
print(f"✔ Detected source folder: {source_folder}")

output_folder = r"C:\Users\w10\Desktop\WebScrapping\filtered_downloads"
# Ask user for minimum count (views/likes)
try:
    MIN_COUNT = int(input("Minimum view/like count दर्ज करें: "))
except:
    print("❌ Invalid number!")
    exit()

os.makedirs(output_folder, exist_ok=True)

# ====== Helper Functions ======
def get_views(data):
    return data.get("node", {}).get("video_view_count", 0)

def get_likes(data):
    return data.get("node", {}).get("edge_media_preview_like", {}).get("count", 0)

def get_caption(data):
    edges = data.get("node", {}).get("edge_media_to_caption", {}).get("edges", [])
    if edges:
        return edges[0].get("node", {}).get("text", "")
    return ""

def load_json(file_path):
    """Load normal JSON or .xz compressed JSON."""
    if file_path.endswith(".xz"):
        with lzma.open(file_path, "rt", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

# ====== Process Files ======
copied_count = 0

for file_name in os.listdir(source_folder):
    file_path = os.path.join(source_folder, file_name)

    if file_name.endswith(".json") or file_name.endswith(".json.xz"):
        try:
            data = load_json(file_path)
            views = get_views(data)
            likes = get_likes(data)

            if views >= MIN_COUNT or likes >= MIN_COUNT:
                base_name = os.path.splitext(file_name)[0].replace(".json","")
                post_folder = os.path.join(output_folder, base_name)
                os.makedirs(post_folder, exist_ok=True)

                # Copy related files
                for ext in [".mp4", ".jpg", ".png", ".txt"]:
                    src_file = os.path.join(source_folder, base_name + ext)
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, post_folder)

                # Save caption
                caption = get_caption(data)
                if caption:
                    with open(os.path.join(post_folder, "caption.txt"), "w", encoding="utf-8") as cf:
                        cf.write(caption)

                copied_count += 1

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

print(f"✔ Filtering complete! {copied_count} items copied to:")
print(output_folder)
