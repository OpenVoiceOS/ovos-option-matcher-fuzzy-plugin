# ovos-reranker-fuzzy-plugin

**Package**: `ovos-reranker-fuzzy-plugin`
**Entry point group**: `opm.agents.reranker`
**Plugin class**: `FuzzyReRankerPlugin` — `ovos_reranker_fuzzy/__init__.py`

## Overview

Implements `ReRankerEngine` from `ovos-plugin-manager` using `rapidfuzz` `WRatio` string similarity. Provides fuzzy ranking of candidate options against a query, with automatic fallback to ordinal/last-word resolution when similarity falls below the configured threshold.

## Key Classes

| Class | File | Description |
|-------|------|-------------|
| `FuzzyReRankerPlugin` | `ovos_reranker_fuzzy/__init__.py:14` | Main plugin; implements `rerank()` and `select_answer()` |

## Public API

### `FuzzyReRankerPlugin.rerank(query, options, lang=None, return_index=False)`

Scores all options against `query` using `rapidfuzz.fuzz.WRatio`. Returns a list of `(score, option_or_index)` tuples sorted by score descending. Scores are normalized to `[0, 1]`.

`FuzzyReRankerPlugin.rerank` — `ovos_reranker_fuzzy/__init__.py:29`

### `FuzzyReRankerPlugin.select_answer(query, options, lang=None, return_index=False)`

Selects the single best match using:
1. Fuzzy match via `ovos_utils.parse.match_one` — accepted if score ≥ `min_conf`.
2. Last-word fallback: if `query` contains "last", "latest", or "final" → returns `options[-1]`.
3. Ordinal fallback: `ovos_number_parser.extract_number(ordinals=True)` → maps to 1-based index.
4. Returns `None` if no strategy matches.

`FuzzyReRankerPlugin.select_answer` — `ovos_reranker_fuzzy/__init__.py:55`

## Configuration

Set under `mycroft.conf` (skills block) or skill settings:

| Key | Default | Description |
|-----|---------|-------------|
| `min_conf` | `0.65` | Minimum score for direct fuzzy acceptance |

## Relation to ovos-workshop

The logic mirrors `_fuzzy_select` in `ovos_workshop/skills/ovos.py:81`, extracted into a standalone OPM-registered plugin so any component can reuse it without importing `ovos-workshop`.
