from app.integrations.lightshell.normalization import (
    normalize_lightshell_name,
)


def test_normalize_case_and_spaces() -> None:
    assert normalize_lightshell_name(
        "  HQD   В АССОРТИМЕНТЕ  "
    ) == "hqd в ассортименте"


def test_normalize_decimal_separator() -> None:
    assert normalize_lightshell_name(
        "HQD 0,45"
    ) == normalize_lightshell_name(
        "hqd 0.45"
    )


def test_normalize_yo_letter() -> None:
    assert normalize_lightshell_name(
        "Чёрный чай"
    ) == normalize_lightshell_name(
        "черный чай"
    )


def test_remove_invisible_characters() -> None:
    assert normalize_lightshell_name(
        "Энер\u00adгетик"
    ) == "энергетик"


def test_normalize_punctuation() -> None:
    assert normalize_lightshell_name(
        "Lipton: лимон; 0,5!"
    ) == "lipton лимон 0 5"