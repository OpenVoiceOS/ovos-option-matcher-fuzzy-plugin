# Copyright 2024, OpenVoiceOS
# Apache 2.0

from typing import List, Optional, Tuple, Union

from ovos_plugin_manager.templates.agents import ReRankerEngine
from ovos_utils.parse import match_one


class FuzzyReRankerPlugin(ReRankerEngine):
    """ReRankerEngine that uses rapidfuzz similarity for ranking and falls back
    to ordinal/last-word resolution when no match exceeds min_conf.

    Config keys (under skill settings or mycroft.conf skills block):
        min_conf (float): minimum fuzzy-match confidence (default 0.65)
    """

    def rerank(self, query: str, options: List[str],
               lang: Optional[str] = None,
               return_index: bool = False) -> List[Tuple[float, Union[str, int]]]:
        """Score all options against query using rapidfuzz; return sorted (score, option) pairs.

        Args:
            query (str): The search or selection query.
            options (List[str]): Potential candidates to rank.
            lang (Optional[str]): Language code (unused, reserved for future use).
            return_index (bool): If True, returns the option index instead of text in the tuple.

        Returns:
            List[Tuple[float, Union[str, int]]]: Sorted list of (score, option/index) pairs,
            highest score first. Scores are normalized to [0, 1].
        """
        from rapidfuzz.process import cdist
        from rapidfuzz import fuzz

        scores = cdist([query], options, scorer=fuzz.WRatio)[0]
        # normalize to [0,1]
        normalized = [float(s) / 100.0 for s in scores]
        if return_index:
            ranked = sorted(enumerate(normalized), key=lambda x: x[1], reverse=True)
            return [(score, idx) for idx, score in ranked]
        ranked = sorted(zip(normalized, options), key=lambda x: x[0], reverse=True)
        return ranked

    def select_answer(self, query: str,
                      options: List[str],
                      lang: Optional[str] = None,
                      return_index: bool = False) -> Optional[Union[str, int]]:
        """Select the best option using fuzzy match, with ordinal/last-word fallback.

        Falls back to ordinal resolution ("second", "last", "option 3") when no
        option scores above min_conf.  Returns None if nothing matches.

        Args:
            query (str): The query to match against options.
            options (List[str]): List of possible answers.
            lang (Optional[str]): Language code for ordinal number parsing.
            return_index (bool): Whether to return the index of the option or the text.

        Returns:
            Optional[Union[str, int]]: The matched option string or index, or None if no match.
        """
        from ovos_number_parser import extract_number

        min_conf = self.config.get("min_conf", 0.65)

        match, score = match_one(query, options)
        if score >= min_conf:
            if return_index:
                return options.index(match)
            return match

        # ordinal/last-word fallback
        q_lower = query.lower()
        last_words = {"last", "latest", "final"}
        if any(w in q_lower for w in last_words):
            return len(options) - 1 if return_index else options[-1]

        num = extract_number(query, ordinals=True, lang=lang or "en-us")
        if num and 1 <= num <= len(options):
            idx = int(num) - 1
            return idx if return_index else options[idx]

        return None
