from faster_whisper import WhisperModel


def transcribe_audio(audio_path: str):
    """
    Transcribe audio using Faster-Whisper.
    Returns detected language and timestamped segments.
    """

    print("\n[STEP 3] Loading Whisper model...")

    # Start with the small model.
    # It gives a good balance between speed and accuracy.
    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

    print("✓ Whisper model loaded")
    print("\nTranscribing audio...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True
    )

    detected_language = info.language
    language_probability = info.language_probability

    print(f"\n✓ Detected language: {detected_language}")
    print(f"✓ Language probability: {language_probability:.2f}")

    results = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            results.append({
                "start": segment.start,
                "end": segment.end,
                "text": text
            })

            print(
                f"[{segment.start:.2f}s -> {segment.end:.2f}s] "
                f"{text}"
            )

    print(f"\n✓ Transcription completed!")
    print(f"✓ Segments detected: {len(results)}")

    return detected_language, results