from src.downloader import download_video
from src.audio import extract_audio


def main():
    url = input("Enter YouTube URL: ").strip()

    if not url:
        print("Please enter a YouTube URL.")
        return

    try:
        # Step 1
        video_path = download_video(url)

        # Step 2
        audio_path = extract_audio(video_path)

        print("\n================================")
        print("✓ STEP 1 + STEP 2 COMPLETED")
        print("================================")
        print(f"Video: {video_path}")
        print(f"Audio: {audio_path}")

    except Exception as e:
        print(f"\n❌ Pipeline failed:")
        print(e)


if __name__ == "__main__":
    main()