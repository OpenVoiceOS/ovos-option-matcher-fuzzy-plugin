# ovos-reranker-fuzzy-plugin

Fuzzy-match `ReRankerEngine` plugin for [OpenVoiceOS](https://openvoiceos.org).

Uses [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) `WRatio` similarity for scoring, with automatic fallback to ordinal/last-word resolution when no candidate clears the confidence threshold.

## Install

```bash
pip install ovos-reranker-fuzzy-plugin
```

Or from source:

```bash
pip install -e .
```

## Usage

```python
from ovos_reranker_fuzzy import FuzzyReRankerPlugin

reranker = FuzzyReRankerPlugin()

options = ["play jazz music", "play rock music", "play classical music"]

# Rank all options
ranked = reranker.rerank("jazz", options)
# [(0.9, "play jazz music"), (0.6, "play rock music"), ...]

# Select best match
best = reranker.select_answer("jazz", options)
# "play jazz music"

# Ordinal fallback
best = reranker.select_answer("the second one", options)
# "play rock music"

# Last-word fallback
best = reranker.select_answer("the last option", options)
# "play classical music"
```

## Configuration

Config keys set under `mycroft.conf` skills block or skill settings:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_conf` | float | `0.65` | Minimum fuzzy-match score to accept a direct match. Below this, ordinal/last-word fallback is attempted. |

## Entry Point

Registered under `opm.agents.reranker`:

```
ovos-reranker-fuzzy-plugin = ovos_reranker_fuzzy:FuzzyReRankerPlugin
```

## License

Apache 2.0
