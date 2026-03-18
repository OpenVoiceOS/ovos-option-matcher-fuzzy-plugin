# How it works

`FuzzyOptionMatcherPlugin.match_option(utterance, options, lang)` runs four stages in order. The first stage that produces a match returns immediately; if nothing matches, `None` is returned.

---

## Stage 1 — Fuzzy match

Uses [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) `WRatio` similarity (via `ovos_utils.parse.match_one`) to score the utterance against every option. If the best score is ≥ `min_conf` (default `0.65`), that option is returned.

```
utterance: "I want pasta please"
options:   ["pizza", "pasta", "salad"]

WRatio("I want pasta please", "pizza") → 0.47
WRatio("I want pasta please", "pasta") → 0.72  ← best, ≥ 0.65 → return "pasta"
WRatio("I want pasta please", "salad") → 0.41
```

This handles synonyms, paraphrasing, filler words, and minor misspellings without any language-specific logic.

**When it fails**: the score falls below `min_conf` — typically when the user gives a reference ("the second one") rather than naming the option directly.

---

## Stage 2 — Last-option vocab

Checks whether any word or phrase from `locale/<lang>/last.voc` appears in the utterance. If so, returns `options[-1]`.

```
utterance: "the last one please"
last.voc (en-us): final, last, latest

"last" found → return options[-1]
```

`last.voc` is translated for every supported language. For German, it contains *letzte*, *letzten*, etc.; for Spanish, *final*, *último*, etc.

---

## Stage 3 — Ordinal and cardinal vocab

Checks the utterance against `.voc` files for positions 1–10:

| Position | Ordinal file | Cardinal file |
|----------|-------------|---------------|
| 1st | `first.voc` | `one.voc` |
| 2nd | `second.voc` | `two.voc` |
| … | … | … |
| 10th | `tenth.voc` | `ten.voc` |

Both files are merged per position. The matcher scans the utterance for every phrase in both files and picks the **longest matching phrase**. Longer phrases win because ordinal `.voc` files also contain multi-word entries:

```
locale/en-us/second.voc:
  second
  second one      ← also here
  number two
  option two

utterance: "the second one"
  "one"        → matches position 0 (one.voc), length 3
  "second"     → matches position 1 (second.voc), length 6
  "second one" → matches position 1 (second.voc), length 10  ← wins

→ return options[1]
```

This eliminates false positives ("one" in "second one") without any regex or word-boundary logic — the multi-word entry in the `.voc` file does the work.

---

## Stage 4 — Numeric fallback (optional)

If `ovos-number-parser` is installed, calls `extract_number(utterance, ordinals=True, lang=lang)`. Handles:

- Raw digits: *"option 7"*, *"number 11"*
- Ordinals beyond ten: *"the twelfth one"*
- Language-specific number words not in the `.voc` files

```
utterance: "option 7"
options:   ["a", "b", "c", "d", "e", "f", "g", "h"]

extract_number("option 7") → 7.0
7 ≤ len(options) → return options[6]  # "g"
```

If `ovos-number-parser` is not installed, this stage is skipped silently.

---

## Fallback behaviour summary

```
match_option("the second one", ["pizza", "pasta", "salad"])

Stage 1: WRatio("the second one", "pizza") = 0.38 < 0.65 → no
         WRatio("the second one", "pasta") = 0.41 < 0.65 → no
         WRatio("the second one", "salad") = 0.35 < 0.65 → no
Stage 2: "last"/"final"/"latest" not in "the second one" → no
Stage 3: "second one" in "the second one" → position 1 → "pasta" ✓
```

```
match_option("something random", ["pizza", "pasta", "salad"])

Stage 1: all scores < 0.65 → no
Stage 2: no last-vocab hit → no
Stage 3: no position vocab hit → no
Stage 4: extract_number("something random") → None → no
→ return None
```

---

## Configuration effect on stages

`min_conf` only affects Stage 1. Stages 2–4 always run if Stage 1 fails, regardless of `min_conf`.

Setting `min_conf: 0.0` causes Stage 1 to always return the highest-scoring option (never falls through to vocab stages). Setting `min_conf: 1.0` disables fuzzy matching entirely.

---

## Source reference

- `FuzzyOptionMatcherPlugin.match_option` — `ovos_option_matcher_fuzzy/__init__.py`
- `_load_last_vocab(lang)` — loads and caches `last.voc`
- `_load_position_vocab(lang)` — loads and caches all ordinal/cardinal `.voc` files into a `Dict[int, Set[str]]`
