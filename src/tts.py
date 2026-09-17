from pathlib import Path
import asyncio
import edge_tts
import subprocess


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

    print("\n[STEP 5] Generating English speech for segments...")

    output_dir = Path("temp/tts_segments")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_segments = []

    for i, segment in enumerate(translated_segments, start=1):

        text = segment["translated_text"]

        if not text.strip():
            continue

        output_file = output_dir / f"segment_{i}.mp3"

        print(f"\nSegment {i}")
        print(f"Text: {text}")
        print(f"Output: {output_file}")

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

        print("✓ Generated")

    print("\n✓ All TTS segments generated!")
    print(f"✓ Segments: {len(generated_segments)}")

    return generated_segments