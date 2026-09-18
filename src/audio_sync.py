from pathlib import Path
import subprocess


CHUNK_SIZE = 30


def get_audio_duration(audio_path: str) -> float:
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


def run_ffmpeg(command):
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        print("\n❌ FFmpeg failed.")
        print(e.stderr)
        raise


def create_synchronized_audio(
    tts_segments,
    output_path="temp/dubbed_audio.wav",
):
    """
    Synchronize TTS segments using small FFmpeg chunks.

    This avoids:
    - Windows command-line length errors
    - -filter_complex_script
    - hundreds of FFmpeg processes
    """

    print("\n[STEP 6] AUDIO SYNCHRONIZATION")
    print("-" * 60)

    if not tts_segments:
        raise ValueError("No TTS segments found.")

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sync_dir = Path("temp/audio_sync")
    sync_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove previous chunk files
    for file in sync_dir.glob("chunk_*.wav"):
        try:
            file.unlink()
        except PermissionError:
            pass

    total_segments = len(tts_segments)

    total_duration = max(
        float(segment["end"])
        for segment in tts_segments
    )

    print(f"→ Total TTS segments: {total_segments}")
    print(f"→ Target duration: {total_duration:.2f} seconds")
    print(f"→ Chunk size: {CHUNK_SIZE} segments")
    print()

    chunk_files = []

    # ---------------------------------------------------------
    # PROCESS CHUNKS
    # ---------------------------------------------------------

    for chunk_start in range(
        0,
        total_segments,
        CHUNK_SIZE,
    ):

        chunk_end = min(
            chunk_start + CHUNK_SIZE,
            total_segments,
        )

        chunk = tts_segments[
            chunk_start:chunk_end
        ]

        chunk_number = (
            chunk_start // CHUNK_SIZE
        ) + 1

        total_chunks = (
            total_segments + CHUNK_SIZE - 1
        ) // CHUNK_SIZE

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"→ Processing chunk "
            f"{chunk_number}/{total_chunks}"
        )

        print(
            f"  Segments: "
            f"{chunk_start + 1} → {chunk_end}"
        )

        # -----------------------------------------------------
        # CHUNK TIMING
        # -----------------------------------------------------

        chunk_start_time = float(
            chunk[0]["start"]
        )

        chunk_end_time = max(
            float(segment["end"])
            for segment in chunk
        )

        chunk_duration = (
            chunk_end_time -
            chunk_start_time
        )

        print(
            f"  Timeline: "
            f"{chunk_start_time:.2f}s → "
            f"{chunk_end_time:.2f}s"
        )

        print(
            f"  Duration: "
            f"{chunk_duration:.2f}s"
        )

        # -----------------------------------------------------
        # BUILD INPUTS
        # -----------------------------------------------------

        command = [
            "ffmpeg",
            "-y",
        ]

        for segment in chunk:

            command.extend([
                "-i",
                str(segment["audio"]),
            ])

        # -----------------------------------------------------
        # BUILD FILTER GRAPH
        # -----------------------------------------------------

        filters = []

        mix_inputs = []

        for index, segment in enumerate(chunk):

            start_time = float(
                segment["start"]
            )

            delay = max(
                0,
                int(
                    (
                        start_time -
                        chunk_start_time
                    ) * 1000
                )
            )

            filters.append(
                f"[{index}:a]"
                f"adelay={delay}|{delay},"
                f"apad,"
                f"atrim=duration={chunk_duration}"
                f"[a{index}]"
            )

            mix_inputs.append(
                f"[a{index}]"
            )

        # -----------------------------------------------------
        # MIX ALL TTS SEGMENTS
        # -----------------------------------------------------

        filter_complex = (
            ";".join(filters)
            + ";"
            + "".join(mix_inputs)
            + f"amix="
            f"inputs={len(chunk)}:"
            f"duration=longest:"
            f"normalize=0,"
            f"atrim=duration={chunk_duration}"
            f"[out]"
        )

        chunk_file = (
            sync_dir /
            f"chunk_{chunk_number:04d}.wav"
        )

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
            str(chunk_file),
        ])

        print(
            "  → Running FFmpeg..."
        )

        run_ffmpeg(command)

        print(
            f"  ✓ Chunk created: "
            f"{chunk_file}"
        )

        chunk_files.append(
            {
                "path": chunk_file,
                "start": chunk_start_time,
                "end": chunk_end_time,
            }
        )

    # ---------------------------------------------------------
    # ADD GAPS BETWEEN CHUNKS
    # ---------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "→ Combining synchronized chunks..."
    )

    timeline_files = []

    current_time = 0.0

    for index, chunk in enumerate(
        chunk_files,
        start=1,
    ):

        chunk_start = chunk["start"]

        # Add silence if there is a gap
        if chunk_start > current_time:

            silence_duration = (
                chunk_start -
                current_time
            )

            silence_file = (
                sync_dir /
                f"gap_{index:04d}.wav"
            )

            print(
                f"  → Gap before chunk "
                f"{index}: "
                f"{silence_duration:.2f}s"
            )

            create_silent_audio(
                silence_duration,
                str(silence_file),
            )

            timeline_files.append(
                silence_file
            )

        timeline_files.append(
            chunk["path"]
        )

        current_time = chunk["end"]

    # ---------------------------------------------------------
    # FINAL SILENCE
    # ---------------------------------------------------------

    if current_time < total_duration:

        remaining = (
            total_duration -
            current_time
        )

        final_silence = (
            sync_dir /
            "final_silence.wav"
        )

        print(
            f"  → Final silence: "
            f"{remaining:.2f}s"
        )

        create_silent_audio(
            remaining,
            str(final_silence),
        )

        timeline_files.append(
            final_silence
        )

    # ---------------------------------------------------------
    # CREATE CONCAT FILE
    # ---------------------------------------------------------

    concat_file = (
        sync_dir /
        "chunks_concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8",
    ) as f:

        for audio_file in timeline_files:

            absolute_path = (
                audio_file
                .resolve()
                .as_posix()
            )

            f.write(
                f"file '{absolute_path}'\n"
            )

    print(
        "→ Concatenating chunks with FFmpeg..."
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]

    run_ffmpeg(command)

    # ---------------------------------------------------------
    # VERIFY DURATION
    # ---------------------------------------------------------

    final_duration = get_audio_duration(
        str(output_path)
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✓ AUDIO SYNCHRONIZATION COMPLETED"
    )

    print(
        f"✓ Output: {output_path}"
    )

    print(
        f"✓ Target duration: "
        f"{total_duration:.2f}s"
    )

    print(
        f"✓ Output duration: "
        f"{final_duration:.2f}s"
    )

    difference = abs(
        total_duration -
        final_duration
    )

    print(
        f"✓ Difference: "
        f"{difference:.3f}s"
    )

    if difference > 0.1:
        print(
            "⚠ Warning: duration difference "
            "is greater than 0.1 seconds."
        )
    else:
        print(
            "✓ Duration synchronization verified."
        )

    return str(output_path)


def create_silent_audio(
    duration: float,
    output_path: str,
):
    """
    Create silent WAV audio.
    """

    if duration <= 0:
        return

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=16000:cl=mono",
        "-t",
        str(duration),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        output_path,
    ]

    run_ffmpeg(command)