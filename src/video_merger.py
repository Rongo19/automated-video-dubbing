from pathlib import Path
import subprocess


def merge_dubbed_audio(
    video_path: str,
    dubbed_audio_path: str,
    output_path: str
):
    """
    Preserve the original soundtrack at low volume
    and mix the English dubbed audio on top.
    """

    print("→ Loading original video...")
    print("→ Loading original audio...")
    print("→ Loading English dubbed audio...")
    print("→ Lowering original audio...")
    print("→ Mixing English dubbing...")
    print("→ Copying original video stream...")

    video = Path(video_path)
    dubbed_audio = Path(dubbed_audio_path)
    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",

        # Original video + audio
        "-i",
        str(video),

        # English dubbed audio
        "-i",
        str(dubbed_audio),

        "-filter_complex",

        (
            "[0:a]volume=0.08[original];"
            "[1:a]volume=1.5[dubbed];"
            "[original][dubbed]"
            "amix=inputs=2:"
            "duration=longest:"
            "dropout_transition=0:"
            "normalize=0"
            "[mixed]"
        ),

        # Keep original video
        "-map",
        "0:v:0",

        # Use mixed audio
        "-map",
        "[mixed]",

        # Do NOT re-encode video
        "-c:v",
        "copy",

        # Encode audio
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

        print("❌ FFmpeg video merge failed.")
        print(e.stderr)

        raise

    print("✓ Original video stream preserved")
    print("✓ Original soundtrack retained at low volume")
    print("✓ English dubbed audio mixed")
    print("✓ Final video created")

    return str(output)