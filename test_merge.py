from src.video_merger import merge_dubbed_audio


video_path = (
    "temp\30 minutes French Listening Practice , REAL French conversation 🇫🇷 [EN⧸FR SUBTITLES] #14.mp4"
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