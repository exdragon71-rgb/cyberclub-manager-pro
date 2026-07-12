import re
import unicodedata


_INVISIBLE_CHARACTERS = str.maketrans(
    {
        "\u00ad": "",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "\ufffe": "",
    }
)


def normalize_lightshell_name(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKC",
        value,
    )

    normalized = normalized.translate(
        _INVISIBLE_CHARACTERS
    )

    normalized = (
        normalized
        .casefold()
        .replace("ё", "е")
    )

    normalized = re.sub(
        r"[^\w]+",
        " ",
        normalized,
        flags=re.UNICODE,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    return normalized