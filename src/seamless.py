import torch
import torchaudio
from transformers import AutoProcessor, SeamlessM4Tv2Model


MODEL_NAME = "facebook/seamless-m4t-v2-large"


def translate_audio_to_english(audio_path: str):
    """
    Translate speech audio directly into English text
    using Meta's SeamlessM4T v2.
    """

    print("\n[STEP 3] Loading SeamlessM4T v2...")
    print(f"Model: {MODEL_NAME}")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Device: {device}")

    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    model = SeamlessM4Tv2Model.from_pretrained(
        MODEL_NAME
    ).to(device)

    print("✓ SeamlessM4T v2 loaded")

    print("\nLoading audio...")

    audio, sample_rate = torchaudio.load(audio_path)

    # Convert stereo → mono
    if audio.shape[0] > 1:
        audio = audio.mean(dim=0, keepdim=True)

    # SeamlessM4T expects 16 kHz audio
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(
            sample_rate,
            16000
        )
        audio = resampler(audio)

    audio = audio.squeeze(0)

    print("✓ Audio loaded")

    print("\nTranslating speech → English text...")

    inputs = processor(
        audios=audio.numpy(),
        sampling_rate=16000,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
        if hasattr(value, "to")
    }

    output_tokens = model.generate(
        **inputs,
        tgt_lang="eng",
        generate_speech=False
    )

    english_text = processor.decode(
        output_tokens[0].tolist(),
        skip_special_tokens=True
    )

    print("\n✓ Translation completed!")

    print("\n================================")
    print("ENGLISH TRANSLATION")
    print("================================")
    print(english_text)

    return english_text