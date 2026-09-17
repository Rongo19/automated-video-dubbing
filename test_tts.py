import asyncio
import edge_tts


async def generate_test_voice():
    text = "Hello! This is a test of the English voice for our automated video dubbing system."

    voice = "en-US-AriaNeural"

    output_file = "temp/test_voice.mp3"

    print("\n[STEP 5] Generating English speech...")
    print(f"Voice: {voice}")

    communicate = edge_tts.Communicate(
        text,
        voice
    )

    await communicate.save(output_file)

    print("✓ TTS generation completed!")
    print(f"✓ Saved to: {output_file}")


asyncio.run(generate_test_voice())