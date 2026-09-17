from src.video_merger import merge_dubbed_audio


video_path = (
    "temp/Everyday Conversation in Slow French 🦥.mp4"
)

dubbed_audio_path = "temp/dubbed_audio.wav"

output_path = "output/final_dubbed_video.mp4"


final_video = merge_dubbed_audio(
    video_path,
    dubbed_audio_path,
    output_path
)


print("\n================================")
print("FINAL VIDEO")
print("================================")
print(f"Video: {final_video}")