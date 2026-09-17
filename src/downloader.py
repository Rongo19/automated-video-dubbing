from pathlib import Path
import yt_dlp


def download_video(url: str) -> str:
    output_dir = Path("temp")
    output_dir.mkdir(exist_ok=True)

    output_template = str(output_dir / "%(title)s.%(ext)s")

    options = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    print("\n[STEP 1] Downloading YouTube video...")
    print(f"URL: {url}\n")

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

        # If yt-dlp merged the streams into MP4
        mp4_file = Path(filename).with_suffix(".mp4")

        if mp4_file.exists():
            filename = str(mp4_file)

    print("\n✓ Download completed!")
    print(f"✓ Saved to: {filename}")

    return filename