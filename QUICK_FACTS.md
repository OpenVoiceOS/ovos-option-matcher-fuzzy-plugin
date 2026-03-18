# QUICK_FACTS — ovos-reranker-fuzzy-plugin

| Field | Value |
|-------|-------|
| Package name | `ovos-reranker-fuzzy-plugin` |
| Python package | `ovos_reranker_fuzzy` |
| Version | `0.0.1a1` (`ovos_reranker_fuzzy/version.py`) |
| Entry point group | `opm.agents.reranker` |
| Entry point key | `ovos-reranker-fuzzy-plugin` |
| Plugin class | `FuzzyReRankerPlugin` |
| Base class | `ReRankerEngine` (`ovos_plugin_manager.templates.agents`) |
| Key dependency | `rapidfuzz`, `ovos-number-parser`, `ovos-plugin-manager<3.0.0` |
| License | Apache 2.0 |
| Min Python | 3.10 |
| Config key | `min_conf` (float, default `0.65`) |
| Test file | `test/test_fuzzy_reranker.py` (10 tests) |
