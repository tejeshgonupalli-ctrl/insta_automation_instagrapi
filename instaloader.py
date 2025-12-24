
# FIRST RUN AUTOMATION SCRIPT

import subprocess
import shutil
import sys
import time
import random
from pathlib import Path


def check_instaloader():
    # Check if instaloader is installed
    if shutil.which('instaloader') is None:
        print("Error: instaloader not found. Install it with: pip install instaloader")
        sys.exit(1)


def build_command(profile: str, target_folder: str, download_posts: bool, download_reels: bool, login: str | None, fast_update: bool):
    # Build the instaloader command
    cmd = ['instaloader']

    cmd += ['--dirname-pattern', str(Path(target_folder).resolve()) + '/{target}']

    if fast_update:
        cmd.append('--fast-update')

    if not download_posts:
        cmd.append('--no-posts')

    if download_reels:
        cmd.append('--reels')

    cmd.append('--no-video-thumbnails')

    if login:
        cmd += ['--login', login]

    cmd.append(profile)
    return cmd


def run_instaloader(cmd):
    print('Running:', ' '.join(cmd))
    try:
        result = subprocess.run(cmd)
        sleep_time = random.randint(3, 7)
        print(f"Waiting for {sleep_time} seconds to avoid rate limit...")
        time.sleep(sleep_time)
        return result.returncode == 0
    except KeyboardInterrupt:
        print('Cancelled by user')
        return False
    except Exception as e:
        print('Error running instaloader:', e)
        return False


def main():
    check_instaloader()

    # Ask for username
    profile = input("Enter Instagram username: ").strip()
    if not profile:
        print("Username cannot be empty")
        return

    # Ask user what to download
    print("\nWhat do you want to download?")
    print("Options: 'post' (only posts), 'reels' (only reels), 'all' (both posts and reels)")
    choice = input("Enter your choice: ").strip().lower()

    if choice == 'post':
        download_posts = True
        download_reels = False
    elif choice == 'reels':
        download_posts = False
        download_reels = True
    elif choice == 'all':
        download_posts = True
        download_reels = True
    else:
        print("Invalid choice. Defaulting to download both posts and reels.")
        download_posts = True
        download_reels = True

    # Auto create target folder
    target_folder = "insta_downloads"
    Path(target_folder).mkdir(parents=True, exist_ok=True)

    login = None  
    num_runs = 3 
    for run in range(1, num_runs + 1):
        print(f"\n=== Run {run} of {num_runs} ===")
    
        fast_update = True  # skip already downloaded media
        cmd = build_command(profile, target_folder, download_posts, download_reels, login, fast_update)
    
        ok = run_instaloader(cmd)
    
        if not ok:
            print("Errors occurred in this run.")
    
        if run < num_runs:
            wait_time = 30  # seconds wait wait
            print(f"Waiting for {wait_time // 60} minutes before next run to avoid rate-limit...")
            time.sleep(wait_time)

    print('Download finished. Check the folder:', Path(target_folder).resolve() / profile)


if __name__ == '__main__':
    main()
