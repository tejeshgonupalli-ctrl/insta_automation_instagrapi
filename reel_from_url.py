import yt_dlp

def download_reel(url, output="posts/reel.mp4"):
    ydl_opts = {
        "outtmpl": output,
        "quiet": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# -------- RUN DIRECTLY --------
if __name__ == "__main__":
    REEL_URL = "https://www.instagram.com/p/DSnm06fEnO2/"
    download_reel(REEL_URL)
    print("✅ Reel downloaded successfully")
