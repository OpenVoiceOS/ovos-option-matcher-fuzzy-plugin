# Copyright 2024, OpenVoiceOS
# Apache 2.0

import os
from functools import lru_cache
from typing import List, Optional, Set

from langcodes import tag_distance
from numtag import Kind, Reason, tag_numbers
from ovos_plugin_manager.templates.agents import OptionMatcherEngine
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.parse import match_one

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")


def _read_voc(path: str) -> Set[str]:
    """Read a .voc file into a set of lowercase stripped strings."""
    with open(path, encoding="utf-8") as fh:
        return {line.strip().lower() for line in fh if line.strip()}


@lru_cache(maxsize=1)
def _available_langs() -> List[str]:
    """Return canonical BCP-47 tags for all locale directories present on disk."""
    try:
        return [standardize_lang_tag(d) for d in os.listdir(_LOCALE_DIR)
                if os.path.isdir(os.path.join(_LOCALE_DIR, d))]
    except OSError:
        return ["en-US"]


def _best_lang(lang: str) -> str:
    """Return the closest available locale directory tag for *lang*.

    Uses :func:`langcodes.tag_distance` to find the best match among the
    locale directories shipped with this plugin, falling back to ``en-US``.
    """
    lang = standardize_lang_tag(lang)
    available = _available_langs()
    if lang in available:
        return lang
    best, best_dist = None, 100000
    for candidate in available:
        dist = tag_distance(lang, candidate)
        if dist < best_dist:
            best, best_dist = candidate, dist
    if best is None or best_dist > 10:
        raise ValueError(f"Unsupported language: {lang!r}. Available: {available}")
    return best


@lru_cache(maxsize=32)
def _load_last_vocab(lang: str) -> Set[str]:
    """Load last.voc for the locale closest to *lang*.

    Args:
        lang: BCP-47 language tag (any casing).

    Returns:
        Set of lowercase words/phrases meaning "last" in that language.
    """
    resolved = _best_lang(lang)
    path = os.path.join(_LOCALE_DIR, resolved, "last.voc")
    if os.path.isfile(path):
        return _read_voc(path)
    return {"last", "latest", "final"}


class FuzzyOptionMatcherPlugin(OptionMatcherEngine):
    """OptionMatcherEngine that resolves a user utterance to a predefined slot.

    Resolution order (first match wins):

    1. Fuzzy match via rapidfuzz WRatio — if score >= min_conf.
    2. Locale-aware ``last.voc`` keyword — returns the final option.
    3. Spoken position read by numtag: the first ordinal or cardinal whole
       number from 1 to ``len(options)``, in reading order ("the second
       one", "number seventeen", "option 7").  numtag marks a lone article
       ("uma guitarra") with ``Reason.ARTICLE``; such mentions name no
       position and are skipped.
    4. None if nothing matches.

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
        lang = lang or "en-US"
        min_conf: float = self.config.get("min_conf", 0.65)
        utterance_lower = utterance.lower()

        # 1. Fuzzy match
        match, score = match_one(utterance, options)
        if score >= min_conf:
            return match

        # 2. Last-option vocab
        if any(w in utterance_lower for w in _load_last_vocab(lang)):
            return options[-1]

        # 3. Spoken position
        for mention in tag_numbers(utterance, lang):
            if (mention.kind in (Kind.ORDINAL, Kind.CARDINAL)
                    and mention.value.isdigit()
                    and Reason.ARTICLE not in mention.reasons
                    and 1 <= int(mention.value) <= len(options)):
                return options[int(mention.value) - 1]

        return None
