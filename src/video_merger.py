from pathlib import Path
import subprocess


def merge_dubbed_audio(
    video_path: str,
    dubbed_audio_path: str,
    output_path: str
):
    """
    Replace original audio with dubbed audio
    while copying the original video stream.
    """

    print("→ Loading original video...")
    print("→ Removing original audio...")
    print("→ Adding English dubbed audio...")
    print("→ Copying original video stream...")
    
    video = Path(video_path)
    audio = Path(dubbed_audio_path)
    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        str(video),

        "-i",
        str(audio),

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        "-c:v",
        "copy",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        str(output)
    ]

    try:

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except subprocess.CalledProcessError as e:

        print(
            "❌ FFmpeg video merge failed."
        )

        print(e.stderr)

        raise

    print("✓ Video stream preserved")
    print("✓ English audio added")
    print("✓ Final video created")

    return str(output)