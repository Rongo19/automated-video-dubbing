from pathlib import Path
import yt_dlp


def download_video(url: str) -> str:
    """
    Download a YouTube video using yt-dlp.
    """

    output_dir = Path("temp")
    output_dir.mkdir(exist_ok=True)

    output_template = str(
        output_dir / "%(title)s.%(ext)s"
    )

    options = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    print("→ Connecting to YouTube...")
    print("→ Downloading video and audio...")

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

        mp4_file = Path(filename).with_suffix(".mp4")

        if mp4_file.exists():
            filename = str(mp4_file)

    print("✓ Download completed")
    print(f"✓ Saved to: {filename}")

    return filename