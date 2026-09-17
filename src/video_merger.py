from pathlib import Path
import subprocess


def merge_dubbed_audio(
    video_path: str,
    dubbed_audio_path: str,
    output_path: str = "output/dubbed_video.mp4"
):
    """
    Replace the original video's audio with the
    synchronized English dubbed audio.

    Video is copied without re-encoding.
    """

    print("\n[STEP 7] Creating final dubbed video...")

    video = Path(video_path)
    audio = Path(dubbed_audio_path)
    output = Path(output_path)

    output.parent.mkdir(parents=True, exist_ok=True)

    if not video.exists():
        raise FileNotFoundError(
            f"Video not found: {video}"
        )

    if not audio.exists():
        raise FileNotFoundError(
            f"Dubbed audio not found: {audio}"
        )

    command = [
        "ffmpeg",
        "-y",

        # Original video
        "-i",
        str(video),

        # English dubbed audio
        "-i",
        str(audio),

        # Copy video without re-encoding
        "-map",
        "0:v:0",

        # Use new audio
        "-map",
        "1:a:0",

        "-c:v",
        "copy",

        # Encode WAV → AAC
        "-c:a",
        "aac",
        "-b:a",
        "192k",

        # Match shortest stream
        "-shortest",

        str(output)
    ]

    print("\nMerging video + English audio...")

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except subprocess.CalledProcessError as e:
        print("\n❌ FFmpeg failed while creating the final video.")
        print(e.stderr)
        raise

    print("\n✓ Final video created!")
    print(f"✓ Output: {output}")

    return str(output)