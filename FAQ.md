# FAQ — ovos-reranker-fuzzy-plugin

**Q: What does this plugin do?**
A: It implements `ReRankerEngine` using `rapidfuzz` `WRatio` similarity to rank a list of string options against a query, and selects the best one. When no option meets the confidence threshold, it falls back to ordinal ("second", "third") and last-word ("last", "final") resolution.

**Q: What entry point group does this plugin register under?**
A: `opm.agents.reranker`, key `ovos-reranker-fuzzy-plugin`. Discoverable via `ovos_plugin_manager.agents.find_reranker_plugins()`.

**Q: How is the confidence threshold configured?**
A: Set `min_conf` (float, default `0.65`) in `mycroft.conf` under the skills block, or pass `config={"min_conf": 0.8}` to the constructor.

**Q: What happens when no match exceeds min_conf?**
A: `select_answer` attempts ordinal fallback: checks for "last"/"latest"/"final" keywords, then uses `ovos_number_parser.extract_number(ordinals=True)` to map words like "second" or "third" to 1-based indices. Returns `None` if all strategies fail.

**Q: What scoring algorithm is used?**
A: `rapidfuzz.fuzz.WRatio` via `cdist`, which combines multiple fuzzy matching strategies for best coverage. Scores are normalized from `[0, 100]` to `[0, 1]`.

**Q: How does this relate to `_fuzzy_select` in ovos-workshop?**
A: The logic is extracted directly from `ovos_workshop/skills/ovos.py:81`. This plugin makes the same behaviour available as an OPM-registered reranker, usable by any OVOS component without depending on `ovos-workshop`.

**Q: Does `rerank` use the `lang` parameter?**
A: No, `rerank` ignores `lang` — it is reserved for future locale-aware matching. `select_answer` passes `lang` to `extract_number` for ordinal parsing.

**Q: How do I use return_index=True?**
A: Pass `return_index=True` to either `rerank` or `select_answer`. `rerank` returns `(score, int)` tuples; `select_answer` returns the integer index of the best match instead of the string.
