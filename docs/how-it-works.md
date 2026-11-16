# How it works

`FuzzyOptionMatcherPlugin.match_option(utterance, options, lang)` runs three stages in order. The first stage that produces a match returns immediately. If nothing matches, `None` is returned.

---

## Stage 1: Fuzzy match

Uses [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) `WRatio` similarity (via `ovos_utils.parse.match_one`) to score the utterance against every option. If the best score is ≥ `min_conf` (default `0.65`), that option is returned.

```
utterance: "I want pasta please"
options:   ["pizza", "pasta", "salad"]

WRatio("I want pasta please", "pizza") → 0.47
WRatio("I want pasta please", "pasta") → 0.72  ← best, ≥ 0.65 → return "pasta"
WRatio("I want pasta please", "salad") → 0.41
```

This handles synonyms, paraphrasing, filler words, and minor misspellings without any language-specific logic.

**When it fails**: the score falls below `min_conf`: typically when the user gives a reference ("the second one") rather than naming the option directly.

---

## Stage 2: Last-option vocab

Checks whether any word or phrase from `locale/<lang>/last.voc` appears in the utterance. If so, returns `options[-1]`.

```
utterance: "the last one please"
last.voc (en-US): final, last, latest

"last" found → return options[-1]
```

`last.voc` is translated for every supported language. For German, it contains *letzte*, *letzten*, and other forms. For Spanish, it contains *final*, *último*, and other forms.

---

## Stage 3: Spoken position

Calls `numtag.tag_numbers(utterance, lang)`, which returns every number in the utterance in reading order, with its value, its kind, a confidence and its reasons. The first mention that meets all of these conditions picks the option at that position:

- The kind is ordinal or cardinal.
- The value is a whole number from 1 to `len(options)`.
- The reasons do not include `numtag.Reason.ARTICLE`. numtag gives that reason to an article next to its noun ("uma guitarra", "una guitarra", "einer Gitarre"), which names no position.

```
utterance: "number seventeen"
options:   20 entries

tag_numbers("number seventeen", "en-US") → "seventeen", 17, cardinal, 1.0
1 ≤ 17 ≤ 20 → return options[16]
```

A number out of range picks nothing: "number seventeen" with ten options returns `None`. numtag reads whole words, so "seven" inside "seventeen" is no match. It also reads digits ("option 7") and long ordinals ("the twenty first", "a vigésima primeira", "die einundzwanzigste").

In "the second one", "second" comes before "one", so the pick is position 2.

---

## Fallback behaviour summary

```
match_option("the second one", ["pizza", "pasta", "salad"])

Stage 1: WRatio("the second one", "pizza") = 0.38 < 0.65 → no
         WRatio("the second one", "pasta") = 0.41 < 0.65 → no
         WRatio("the second one", "salad") = 0.35 < 0.65 → no
Stage 2: "last"/"final"/"latest" not in "the second one" → no
Stage 3: numtag reads "second", ordinal 2 → "pasta" (match)
```

```
match_option("something random", ["pizza", "pasta", "salad"])

Stage 1: all scores < 0.65 → no
Stage 2: no last-vocab hit → no
Stage 3: numtag reads no number → no
→ return None
```

---

## Configuration effect on stages

`min_conf` only affects Stage 1. Stages 2-3 always run if Stage 1 fails, regardless of `min_conf`.

Setting `min_conf: 0.0` causes Stage 1 to always return the highest-scoring option (never falls through to the later stages). Setting `min_conf: 1.0` disables fuzzy matching entirely.

---

## Source reference

- `FuzzyOptionMatcherPlugin.match_option`: `ovos_option_matcher_fuzzy/__init__.py:92`
- `_load_last_vocab(lang)`: loads and caches `last.voc`: `ovos_option_matcher_fuzzy/__init__.py:31`
- `_candidate_langs(lang)`: returns `[lang, lang.split("-")[0], "en-us"]` as lookup priority: `ovos_option_matcher_fuzzy/__init__.py:25`

---
[Home](index.md) · [Configuration →](configuration.md)
