from pathlib import Path
import json

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

import torch


MODEL_NAME = "facebook/nllb-200-distilled-600M"

PROGRESS_FILE = Path(
    "temp/translation_progress.json"
)


class NLLBTranslator:

    def __init__(self):

        print("\n[STEP 4] Loading NLLB-200 translator...")
        print(f"Model: {MODEL_NAME}")

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"Device: {self.device}"
        )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_NAME
            )
        )

        self.model = (
            AutoModelForSeq2SeqLM
            .from_pretrained(MODEL_NAME)
            .to(self.device)
        )

        self.model.eval()

        print("✓ NLLB-200 loaded!")

    def translate(
        self,
        text: str,
        source_language: str
    ):

        if not text.strip():
            return ""

        source_code = self.get_language_code(
            source_language
        )

        self.tokenizer.src_lang = source_code

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)

        english_token_id = (
            self.tokenizer.convert_tokens_to_ids(
                "eng_Latn"
            )
        )

        with torch.no_grad():

            translated_tokens = (
                self.model.generate(
                    **inputs,
                    forced_bos_token_id=english_token_id,
                    max_length=512
                )
            )

        translation = (
            self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0]
        )

        return translation

    def get_language_code(
        self,
        language: str
    ):

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
                f"Language '{language}' "
                f"is not configured yet."
            )

        return language_codes[language]


def load_translation_progress():

    if not PROGRESS_FILE.exists():
        return []

    try:
        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_translation_progress(
    translated_segments
):

    PROGRESS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            translated_segments,
            file,
            indent=2,
            ensure_ascii=False
        )


def translate_segments(
    segments,
    source_language
):

    translator = NLLBTranslator()

    print(
        "\nTranslating segments..."
    )

    translated_segments = (
        load_translation_progress()
    )

    if translated_segments:

        print(
            f"⚡ Found "
            f"{len(translated_segments)} "
            f"previously translated segments."
        )

        print(
            "→ Resuming translation..."
        )

    start_index = len(
        translated_segments
    )

    for i in range(
        start_index,
        len(segments)
    ):

        segment = segments[i]

        segment_number = i + 1

        original_text = (
            segment["text"]
        )

        print(
            f"\n→ Translating segment "
            f"{segment_number}/"
            f"{len(segments)}..."
        )

        print(
            f"Original: {original_text}"
        )

        try:

            english_text = translator.translate(
                original_text,
                source_language
            )

            print(
                f"English : {english_text}"
            )

            translated_segments.append({

                "start": segment["start"],

                "end": segment["end"],

                "original_text": original_text,

                "translated_text": english_text

            })

            # Save after EVERY successful segment
            save_translation_progress(
                translated_segments
            )

        except Exception as e:

            print(
                f"\n❌ Translation failed "
                f"at segment "
                f"{segment_number}"
            )

            print(
                f"Error: {e}"
            )

            print(
                "\n✓ Previously translated "
                "segments have been saved."
            )

            print(
                f"✓ Saved segments: "
                f"{len(translated_segments)}"
            )

            raise

    print(
        "\n✓ Translation completed!"
    )

    print(
        f"✓ Total translated segments: "
        f"{len(translated_segments)}"
    )

    return translated_segments