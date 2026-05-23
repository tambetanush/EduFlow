from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request

SUPPORTED_LOCALES = {"en", "hi"}
DEFAULT_LOCALE = "en"
MESSAGE_KEYS = {"message", "detail", "msg", "error"}

LOCALES_ROOT = Path(__file__).resolve().parents[2] / "locales"


def _load_locale(name: str) -> dict[str, Any]:
    path = LOCALES_ROOT / f"{name}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


LOCALE_DATA = {
    "en": _load_locale("en"),
    "hi": _load_locale("hi"),
}

VALIDATION_MAP = {
    "Field required": {
        "en": "Field required",
        "hi": "यह फ़ील्ड आवश्यक है।",
    },
    "Input should be a valid string": {
        "en": "Input should be a valid string",
        "hi": "इनपुट एक मान्य स्ट्रिंग होना चाहिए।",
    },
    "Input should be a valid integer": {
        "en": "Input should be a valid integer",
        "hi": "इनपुट एक मान्य पूर्णांक होना चाहिए।",
    },
    "Input should be a valid number": {
        "en": "Input should be a valid number",
        "hi": "इनपुट एक मान्य संख्या होना चाहिए।",
    },
    "Input should be a valid list": {
        "en": "Input should be a valid list",
        "hi": "इनपुट एक मान्य सूची होना चाहिए।",
    },
    "Input should be a valid dictionary": {
        "en": "Input should be a valid dictionary",
        "hi": "इनपुट एक मान्य डिक्शनरी होना चाहिए।",
    },
}

_DIRECT_MAP = {
    "a": "अ",
    "b": "ब",
    "c": "क",
    "d": "द",
    "e": "ए",
    "f": "फ",
    "g": "ग",
    "h": "ह",
    "i": "इ",
    "j": "ज",
    "k": "क",
    "l": "ल",
    "m": "म",
    "n": "न",
    "o": "ओ",
    "p": "प",
    "q": "क",
    "r": "र",
    "s": "स",
    "t": "ट",
    "u": "उ",
    "v": "व",
    "w": "व",
    "x": "क्स",
    "y": "य",
    "z": "ज़",
}

_CLUSTER_MAP = [
    ("tion", "शन"),
    ("sion", "ज़न"),
    ("ing", "िंग"),
    ("sh", "श"),
    ("ch", "च"),
    ("th", "थ"),
    ("ph", "फ"),
    ("kh", "ख"),
    ("gh", "घ"),
    ("aa", "आ"),
    ("ee", "ई"),
    ("oo", "ऊ"),
    ("ai", "ऐ"),
    ("au", "औ"),
    ("ou", "औ"),
]


def normalize_locale(value: str | None) -> str:
    if value and value.lower().startswith("hi"):
        return "hi"
    return DEFAULT_LOCALE


def get_locale_from_request(request: Request) -> str:
    return normalize_locale(
        request.headers.get("x-language")
        or request.headers.get("accept-language")
        or getattr(request.state, "locale", None)
    )


def _interpolate(text: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return text

    out = text
    for key, value in params.items():
        out = out.replace(f"{{{{{key}}}}}", str(value))
    return out


def _lookup_path(locale: str, path: str) -> str | None:
    node: Any = LOCALE_DATA[locale]
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def translate_key(path: str, locale: str, **params: Any) -> str:
    value = _lookup_path(locale, path) or _lookup_path(DEFAULT_LOCALE, path) or path
    return _interpolate(value, params)


def _transliterate_word(word: str) -> str:
    lower = word.lower()
    index = 0
    out = []

    while index < len(lower):
        cluster = next((item for item in _CLUSTER_MAP if lower.startswith(item[0], index)), None)
        if cluster:
            out.append(cluster[1])
            index += len(cluster[0])
            continue

        out.append(_DIRECT_MAP.get(lower[index], word[index]))
        index += 1

    return "".join(out)


def transliterate_to_hindi(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        segment = match.group(0)
        if re.match(r"^(https?:|www\.|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})$", segment, re.I):
            return segment
        return _transliterate_word(segment)

    return re.sub(r"[A-Za-z][A-Za-z0-9@._/-]*", replace, text)


def translate_text(text: str, locale: str) -> str:
    if locale == "en" or not text:
        return text

    raw_map = LOCALE_DATA[locale].get("raw", {})
    if isinstance(raw_map, dict) and text in raw_map:
        return str(raw_map[text])

    if text in VALIDATION_MAP:
        return VALIDATION_MAP[text][locale]

    return transliterate_to_hindi(text)


def translate_payload(value: Any, locale: str, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {key: translate_payload(item, locale, key) for key, item in value.items()}
    if isinstance(value, list):
        return [translate_payload(item, locale, parent_key) for item in value]
    if isinstance(value, str) and parent_key in MESSAGE_KEYS:
        return translate_text(value, locale)
    return value


def localized_http_exception(status_code: int, detail: str, locale: str, headers: dict[str, str] | None = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail=translate_text(detail, locale), headers=headers)
