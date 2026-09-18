from src.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint
)


print("=" * 60)
print("CHECKPOINT SYSTEM TEST")
print("=" * 60)


print("\n→ Saving checkpoint...")

save_checkpoint({
    "video_path": "temp/test_video.mp4",
    "language": "fr",
    "transcription_completed": True,
    "translation_completed": True
})

print("✓ Checkpoint saved")


print("\n→ Loading checkpoint...")

data = load_checkpoint()

print("✓ Checkpoint loaded")

print("\nCheckpoint data:")

for key, value in data.items():

    print(
        f"  {key}: {value}"
    )


print("\n→ Clearing checkpoint...")

clear_checkpoint()

print("✓ Checkpoint cleared")


print("\n" + "=" * 60)
print("✓ CHECKPOINT TEST COMPLETE")
print("=" * 60)