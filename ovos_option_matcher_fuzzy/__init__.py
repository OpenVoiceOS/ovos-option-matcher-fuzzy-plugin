# Copyright 2024, OpenVoiceOS
# Apache 2.0

import os
from functools import lru_cache
from typing import List, Optional, Set

from ovos_plugin_manager.templates.agents import OptionMatcherEngine
from ovos_utils.parse import match_one

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "locale")


@lru_cache(maxsize=32)
def _load_last_vocab(lang: str) -> Set[str]:
    """Load last.voc for *lang*, falling back to en-us if the file is absent.

    Args:
        lang (str): BCP-47 language tag (e.g. "de-de").

    Returns:
        Set[str]: Lowercase words/phrases that mean "last" in that language.
    """
    for candidate in (lang, lang.split("-")[0], "en-us"):
        path = os.path.join(_LOCALE_DIR, candidate, "last.voc")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                return {line.strip().lower() for line in fh if line.strip()}
    return {"last", "latest", "final"}  # hard fallback — should never be reached


class FuzzyOptionMatcherPlugin(OptionMatcherEngine):
    """OptionMatcherEngine that resolves a user utterance to a predefined slot.

    Uses rapidfuzz similarity as the primary signal, with locale-aware
    last-word and ordinal/numeric fallback resolution.

    Config keys (under skill settings or mycroft.conf skills block):
        min_conf (float): minimum fuzzy-match confidence (default 0.65)
    """

    def match_option(self, utterance: str, options: List[str],
                     lang: Optional[str] = None) -> Optional[str]:
        """Resolve *utterance* to the best matching entry in *options*.

        Resolution order:
        1. Fuzzy match via rapidfuzz WRatio — returns if score >= min_conf.
        2. Last-word vocab (locale/*/last.voc) -> final option.
        3. Ordinal/numeric via ovos-number-parser -> options[n-1].
        4. None if nothing matches.

        Args:
            utterance (str): The raw user response.
            options (List[str]): The predefined slots the skill offered.
            lang (Optional[str]): BCP-47 language code for vocab and ordinal parsing.

        Returns:
            Optional[str]: The matched option string, or None if no match.
        """
        from ovos_number_parser import extract_number

        lang = lang or "en-us"
        min_conf: float = self.config.get("min_conf", 0.65)

        match, score = match_one(utterance, options)
        if score >= min_conf:
            return match

        last_words = _load_last_vocab(lang)
        if any(w in utterance.lower() for w in last_words):
            return options[-1]

        num = extract_number(utterance, ordinals=True, lang=lang)
        if num and 1 <= num <= len(options):
            return options[int(num) - 1]

        return None
