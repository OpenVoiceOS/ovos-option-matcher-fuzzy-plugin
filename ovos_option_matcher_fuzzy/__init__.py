# Copyright 2024, OpenVoiceOS
# Apache 2.0

from typing import List, Optional

from ovos_plugin_manager.templates.agents import OptionMatcherEngine
from ovos_utils.parse import match_one


class FuzzyOptionMatcherPlugin(OptionMatcherEngine):
    """OptionMatcherEngine that resolves a user utterance to a predefined slot.

    Uses rapidfuzz similarity as the primary signal, with ordinal ("second",
    "last") and numeric ("option 3") fallback resolution.

    Config keys (under skill settings or mycroft.conf skills block):
        min_conf (float): minimum fuzzy-match confidence (default 0.65)
    """

    def match_option(self, utterance: str, options: List[str],
                     lang: Optional[str] = None) -> Optional[str]:
        """Resolve *utterance* to the best matching entry in *options*.

        Resolution order:
        1. Fuzzy match via rapidfuzz WRatio — returns immediately if score >= min_conf.
        2. Last-word set ("last", "latest", "final") -> final option.
        3. Ordinal/numeric via ovos-number-parser -> options[n-1].
        4. None if nothing matches.

        Args:
            utterance (str): The raw user response.
            options (List[str]): The predefined slots the skill offered.
            lang (Optional[str]): BCP-47 language code for ordinal parsing.

        Returns:
            Optional[str]: The matched option string, or None if no match.
        """
        from ovos_number_parser import extract_number

        min_conf: float = self.config.get("min_conf", 0.65)

        match, score = match_one(utterance, options)
        if score >= min_conf:
            return match

        q_lower = utterance.lower()
        if any(w in q_lower for w in ("last", "latest", "final")):
            return options[-1]

        num = extract_number(utterance, ordinals=True, lang=lang or "en-us")
        if num and 1 <= num <= len(options):
            return options[int(num) - 1]

        return None
