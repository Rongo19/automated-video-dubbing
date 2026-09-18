import json
from src.transcriber import transcribe_audio

audio_path = "temp/audio.wav"

print("Recovering speech timestamps...")

language, segments = transcribe_audio(audio_path)

data = {
    "language": language,
    "segments": segments
}

with open(
    "temp/timestamps.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\n✓ Timestamps recovered")
print(f"✓ Language: {language}")
print(f"✓ Segments: {len(segments)}")
print("✓ Saved to: temp/timestamps.json")