# Copyright 2024, OpenVoiceOS
# Apache 2.0

import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Set

from ovos_plugin_manager.templates.agents import OptionMatcherEngine
from ovos_utils.parse import match_one

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "locale")

_ORDINAL_NAMES = ["first", "second", "third", "fourth", "fifth",
                  "sixth", "seventh", "eighth", "ninth", "tenth"]
_CARDINAL_NAMES = ["one", "two", "three", "four", "five",
                   "six", "seven", "eight", "nine", "ten"]


def _word_match(word: str, text: str) -> bool:
    """Return True if *word* appears as a whole word in *text*."""
    return bool(re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text))


def _any_word_match(words: Set[str], text: str) -> bool:
    """Return True if any entry in *words* appears as a whole word in *text*."""
    return any(_word_match(w, text) for w in words)


def _read_voc(path: str) -> Set[str]:
    """Read a .voc file into a set of lowercase stripped strings."""
    with open(path, encoding="utf-8") as fh:
        return {line.strip().lower() for line in fh if line.strip()}


def _candidate_langs(lang: str) -> List[str]:
    """Return candidate locale directories to check in priority order."""
    return [lang, lang.split("-")[0], "en-us"]


@lru_cache(maxsize=32)
def _load_last_vocab(lang: str) -> Set[str]:
    """Load last.voc for *lang*, falling back to en-us if absent.

    Args:
        lang: BCP-47 language tag.

    Returns:
        Set of lowercase words meaning "last" in that language.
    """
    for candidate in _candidate_langs(lang):
        path = os.path.join(_LOCALE_DIR, candidate, "last.voc")
        if os.path.isfile(path):
            return _read_voc(path)
    return {"last", "latest", "final"}


@lru_cache(maxsize=32)
def _load_position_vocab(lang: str) -> Dict[int, Set[str]]:
    """Load ordinal and cardinal .voc files for *lang* into a position map.

    Returns a dict mapping 0-based index -> set of words that reference that
    position (e.g. index 0: {"first", "one", ...}).  Falls back through the
    language prefix then en-us for each missing file.

    Args:
        lang: BCP-47 language tag.

    Returns:
        Dict mapping position index (0-based) to a set of trigger words.
    """
    result: Dict[int, Set[str]] = {}
    for i, (ord_name, card_name) in enumerate(zip(_ORDINAL_NAMES, _CARDINAL_NAMES)):
        words: Set[str] = set()
        for voc_name in (ord_name, card_name):
            for candidate in _candidate_langs(lang):
                path = os.path.join(_LOCALE_DIR, candidate, f"{voc_name}.voc")
                if os.path.isfile(path):
                    words |= _read_voc(path)
                    break
        result[i] = words
    return result


class FuzzyOptionMatcherPlugin(OptionMatcherEngine):
    """OptionMatcherEngine that resolves a user utterance to a predefined slot.

    Resolution order (first match wins):
    1. Fuzzy match via rapidfuzz WRatio — if score >= min_conf.
    2. Locale-aware last.voc keyword — returns the final option.
    3. Ordinal/cardinal vocab (first.voc … tenth.voc, one.voc … ten.voc).
    4. Numeric fallback via ovos-number-parser (optional dependency).
    5. None if nothing matches.

    Config keys (under skill settings or mycroft.conf skills block):
        min_conf (float): minimum fuzzy-match confidence (default 0.65).
    """

    def match_option(self, utterance: str, options: List[str],
                     lang: Optional[str] = None) -> Optional[str]:
        """Resolve *utterance* to the best matching entry in *options*.

        Args:
            utterance: The raw user response.
            options: The predefined slots the skill offered.
            lang: BCP-47 language code for vocab and ordinal parsing.

        Returns:
            The matched option string, or None if no match.
        """
        lang = lang or "en-us"
        min_conf: float = self.config.get("min_conf", 0.65)
        utterance_lower = utterance.lower()

        # 1. Fuzzy match
        match, score = match_one(utterance, options)
        if score >= min_conf:
            return match

        # 2. Last-option vocab
        if _any_word_match(_load_last_vocab(lang), utterance_lower):
            return options[-1]

        # 3. Ordinal/cardinal vocab (covers positions 0-9)
        # Collect all matches then pick the one triggered by the longest word
        # (avoids short cardinals like "one" stealing matches from "second one").
        position_vocab = _load_position_vocab(lang)
        best_idx: Optional[int] = None
        best_len = 0
        for idx in range(min(len(options), len(_ORDINAL_NAMES))):
            for word in position_vocab.get(idx, ()):
                if len(word) > best_len and _word_match(word, utterance_lower):
                    best_idx = idx
                    best_len = len(word)
        if best_idx is not None:
            return options[best_idx]

        # 4. Numeric fallback via ovos-number-parser (optional)
        try:
            from ovos_number_parser import extract_number
            num = extract_number(utterance, ordinals=True, lang=lang)
            if num and 1 <= num <= len(options):
                return options[int(num) - 1]
        except ImportError:
            pass

        return None
