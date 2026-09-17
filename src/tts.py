from pathlib import Path
import asyncio
import edge_tts


VOICE = "en-US-AriaNeural"


async def generate_speech(text: str, output_path: str):
    """
    Generate English speech for one text segment.
    """

    communicate = edge_tts.Communicate(
        text,
        VOICE
    )

    await communicate.save(output_path)


def generate_segment_audio(translated_segments):
    """
    Generate TTS audio for every translated segment.
    """

    print("→ Loading English TTS voice...")
    print(f"→ Voice: {VOICE}")

    output_dir = Path("temp/tts_segments")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    generated_segments = []

    total_segments = len(translated_segments)

    print(
        f"→ Generating speech for "
        f"{total_segments} segments..."
    )

    for i, segment in enumerate(
        translated_segments,
        start=1
    ):

        text = segment["translated_text"]

        if not text.strip():
            print(
                f"⚠ Skipping empty segment "
                f"{i}/{total_segments}"
            )
            continue

        output_file = (
            output_dir / f"segment_{i}.mp3"
        )

        print(
            f"\n→ Generating segment "
            f"{i}/{total_segments}"
        )

        print(
            f"  Text: {text}"
        )

        asyncio.run(
            generate_speech(
                text,
                str(output_file)
            )
        )

        generated_segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": text,
            "audio": str(output_file)
        })

        print(
            f"  ✓ Saved: {output_file}"
        )

    print(
        f"\n✓ English speech generation completed"
    )

    print(
        f"✓ Generated segments: "
        f"{len(generated_segments)}/{total_segments}"
    )

    return generated_segments