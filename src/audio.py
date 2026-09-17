from pathlib import Path
import subprocess


def extract_audio(video_path: str) -> str:
    """
    Extract audio from a video and convert it to
    mono 16 kHz WAV format.
    """

    video = Path(video_path)
    audio_path = video.parent / "audio.wav"

    print("\n[STEP 2] Extracting audio...")
    print(f"Input : {video}")
    print(f"Output: {audio_path}")

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

        print("✓ Audio extraction completed!")
        print(f"✓ Saved to: {audio_path}")

        return str(audio_path)

    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg failed while extracting audio.")
        print(e.stderr)
        raise