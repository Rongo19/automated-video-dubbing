from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


MODEL_NAME = "facebook/nllb-200-distilled-600M"


class NLLBTranslator:
    def __init__(self):
        print("\n[STEP 4] Loading NLLB-200 translator...")
        print(f"Model: {MODEL_NAME}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME
        ).to(self.device)

        print("✓ NLLB-200 loaded!")

    def translate(self, text: str, source_language: str) -> str:
        """
        Translate text from the detected language to English.
        """

        if not text.strip():
            return ""

        source_code = self.get_language_code(source_language)

        self.tokenizer.src_lang = source_code

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)

        english_token_id = self.tokenizer.convert_tokens_to_ids(
            "eng_Latn"
        )

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=english_token_id,
            max_length=512
        )

        translation = self.tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )[0]

        return translation

    def get_language_code(self, language: str) -> str:
        """
        Convert Whisper language code to NLLB language code.
        """

        language_codes = {
            "en": "eng_Latn",
            "fr": "fra_Latn",
            "de": "deu_Latn",
            "es": "spa_Latn",
            "it": "ita_Latn",
            "pt": "por_Latn",
            "nl": "nld_Latn",
            "ru": "rus_Cyrl",
            "uk": "ukr_Cyrl",
            "pl": "pol_Latn",
            "tr": "tur_Latn",
            "ar": "arb_Arab",
            "fa": "pes_Arab",
            "hi": "hin_Deva",
            "mr": "mar_Deva",
            "bn": "ben_Beng",
            "gu": "guj_Gujr",
            "ta": "tam_Taml",
            "te": "tel_Telu",
            "kn": "kan_Knda",
            "ml": "mal_Mlym",
            "pa": "pan_Guru",
            "ur": "urd_Arab",
            "ne": "npi_Deva",
            "si": "sin_Sinh",
            "th": "tha_Thai",
            "vi": "vie_Latn",
            "id": "ind_Latn",
            "ms": "zsm_Latn",
            "ja": "jpn_Jpan",
            "ko": "kor_Hang",
            "zh": "zho_Hans"
        }

        if language not in language_codes:
            raise ValueError(
                f"Language '{language}' is not configured yet."
            )

        return language_codes[language]


def translate_segments(segments, source_language):
    """
    Translate all Whisper segments into English.
    """

    translator = NLLBTranslator()

    print("\nTranslating segments...")

    translated_segments = []

    for i, segment in enumerate(segments, start=1):

        original_text = segment["text"]

        print(f"\nSegment {i}")
        print(f"Original: {original_text}")

        try:
            english_text = translator.translate(
                original_text,
                source_language
            )

            print(f"English : {english_text}")

            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "original_text": original_text,
                "translated_text": english_text
            })

        except Exception as e:

            print(f"❌ Translation failed: {e}")

            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "original_text": original_text,
                "translated_text": ""
            })

    print("\n✓ Translation completed!")

    return translated_segments