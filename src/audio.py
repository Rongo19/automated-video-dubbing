from pathlib import Path
import subprocess


def extract_audio(video_path: str) -> str:
    """
    Extract audio from video and convert it to
    mono 16 kHz WAV.
    """

    video = Path(video_path)

    audio_path = (
        video.parent / "audio.wav"
    )

    print("→ Reading video...")
    print("→ Extracting audio stream...")
    print("→ Converting to 16 kHz mono WAV...")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(audio_path),
    ]

    try:

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as e:

        print("❌ FFmpeg audio extraction failed.")
        print(e.stderr)

        raise

    print("✓ Audio extraction completed")
    print(f"✓ Saved to: {audio_path}")

    return str(audio_path)