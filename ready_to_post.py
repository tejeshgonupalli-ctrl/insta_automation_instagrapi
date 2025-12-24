# build_caption.py
import os
from pathlib import Path
import shutil

INPUT_FOLDER = Path(r"C:\Users\w10\Desktop\WebScrapping\filtered_downloads_watermarked")
OUTPUT_FOLDER = Path(r"C:\Users\w10\Desktop\WebScrapping\final_ready_to_post")

OUTPUT_FOLDER.mkdir(exist_ok=True)


def read_file(path):
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def build_final_caption(folder):
    hook = read_file(folder / "hook.txt")
    caption = read_file(folder / "caption.txt")
    cta = read_file(folder / "cta.txt")
    hashtags = read_file(folder / "hashtags.txt")

    final_caption = ""

    if hook:
        final_caption += hook + "\n\n"
    if caption:
        final_caption += caption + "\n\n"
    if cta:
        final_caption += cta + "\n\n"
    if hashtags:
        final_caption += hashtags

    return final_caption.strip()


def process_post_folder(post_folder):
    folder_name = post_folder.name
    out_folder = OUTPUT_FOLDER / folder_name
    out_folder.mkdir(exist_ok=True)

    print(f"Processing: {folder_name}")

    # Copy media files only
    for file in post_folder.iterdir():
        if file.is_file():
            if file.suffix.lower() in [".mp4", ".mov", ".jpg", ".jpeg", ".png"]:
                shutil.copy2(file, out_folder)

    # Build final caption file
    final_caption = build_final_caption(post_folder)

    (out_folder / "final_caption.txt").write_text(final_caption, encoding="utf-8")

    # Delete UTC file from output if exists
    utc_file = out_folder / "UTC.txt"
    if utc_file.exists():
        utc_file.unlink()

    print(f"✔ Done: {folder_name}")


def main():
    posts = [f for f in INPUT_FOLDER.iterdir() if f.is_dir()]

    if not posts:
        print("No folders found in filtered_downloads_watermarked.")
        return

    for post in posts:
        process_post_folder(post)

    print("\nALL DONE! Ready-to-post folders created here:")
    print(OUTPUT_FOLDER.resolve())


if __name__ == "__main__":
    main()
