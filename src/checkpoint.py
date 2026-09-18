import json
from pathlib import Path


CHECKPOINT_FILE = Path("temp/checkpoint.json")


def save_checkpoint(data):
    """
    Save pipeline progress to temp/checkpoint.json.
    """

    CHECKPOINT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CHECKPOINT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_checkpoint():
    """
    Load previous pipeline progress.
    """

    if not CHECKPOINT_FILE.exists():
        return {}

    try:

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


def clear_checkpoint():
    """
    Remove the checkpoint after successful completion.
    """

    if CHECKPOINT_FILE.exists():

        CHECKPOINT_FILE.unlink()