from pathlib import Path
import subprocess


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of an audio file using FFprobe.
    """

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def create_synchronized_audio(
    tts_segments,
    output_path="temp/dubbed_audio.wav",
):
    """
    Place each TTS segment at its original timestamp
    and create one synchronized audio track.
    """

    print("\n[STEP 6] Synchronizing English audio...")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not tts_segments:
        raise ValueError("No TTS segments found.")

    # Total duration comes from the last Whisper segment.
    total_duration = max(
        segment["end"]
        for segment in tts_segments
    )

    print(f"Target duration: {total_duration:.2f} seconds")

    # Build FFmpeg inputs.
    command = ["ffmpeg", "-y"]

    for segment in tts_segments:
        command.extend([
            "-i",
            segment["audio"]
        ])

    # Build filter complex.
    filters = []

    for i, segment in enumerate(tts_segments):

        start_ms = int(segment["start"] * 1000)

        filters.append(
            f"[{i}:a]"
            f"adelay={start_ms}:all=1,"
            f"aformat=sample_fmts=fltp:sample_rates=16000:channel_layouts=mono"
            f"[a{i}]"
        )

    audio_inputs = "".join(
        f"[a{i}]"
        for i in range(len(tts_segments))
    )

    filters.append(
    f"{audio_inputs}"
    f"amix=inputs={len(tts_segments)}:"
    f"duration=longest:"
    f"dropout_transition=0,"
    f"apad,"
    f"atrim=duration={total_duration}"
    f"[out]"
    )

    filter_complex = ";".join(filters)

    command.extend([
        "-filter_complex",
        filter_complex,
        "-map",
        "[out]",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ])

    print("\nCreating synchronized audio...")

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg synchronization failed.")
        print(e.stderr)
        raise

    duration = get_audio_duration(
        str(output_path)
    )

    print("\n✓ Synchronization completed!")
    print(f"✓ Output: {output_path}")
    print(f"✓ Duration: {duration:.2f} seconds")

    return str(output_path)