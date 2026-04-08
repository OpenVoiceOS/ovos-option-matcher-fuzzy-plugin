# Localization

The plugin ships `.voc` files for 15 languages. All locale files live under `locale/<lang>/` and are loaded at runtime — no code changes are needed to add or improve a language.

---

## Supported languages

| Tag | Language | Ordinal/cardinal voc | Multi-word phrases | `last.voc` |
|-----|----------|---------------------|--------------------|------------|
| `ca-ES` | Catalan | ✓ | — | ✓ |
| `cs-CZ` | Czech | ✓ | — | ✓ |
| `da-DK` | Danish | ✓ | — | ✓ |
| `de-DE` | German | ✓ | ✓ | ✓ |
| `en-US` | English | ✓ | ✓ | ✓ |
| `es-ES` | Spanish | ✓ | ✓ | ✓ |
| `eu-ES` | Basque | ✓ | — | ✓ |
| `fr-FR` | French | ✓ | ✓ | ✓ |
| `gl-ES` | Galician | ✓ | — | ✓ |
| `it-IT` | Italian | ✓ | — | ✓ |
| `nl-NL` | Dutch | ✓ | — | ✓ |
| `pl-PL` | Polish | ✓ | — | ✓ |
| `pt-BR` | Portuguese (Brazil) | ✓ | — | ✓ |
| `pt-PT` | Portuguese (Portugal) | ✓ | — | ✓ |
| `sv-SE` | Swedish | ✓ | — | ✓ |

Languages marked **"Multi-word phrases ✓"** have entries like "second one", "número dos" in their ordinal `.voc` files. Languages without them rely on single-word ordinals and the numeric fallback stage.

---

## File structure

```
locale/
  en-US/
    last.voc        ← words meaning "last/final"
    first.voc       ← words/phrases for position 1
    one.voc         ← cardinal words for position 1
    second.voc      ← words/phrases for position 2
    two.voc
    third.voc
    three.voc
    fourth.voc
    four.voc
    fifth.voc
    five.voc
    sixth.voc
    six.voc
    seventh.voc
    seven.voc
    eighth.voc
    eight.voc
    ninth.voc
    nine.voc
    tenth.voc
    ten.voc
```

**Filenames are canonical English** — do not rename them. Only the content is translated.

Each file contains one word or phrase per line, lowercase. Blank lines and leading/trailing whitespace are ignored.

---

## How lookup works

For a given `lang` (e.g. `"de-DE"`), the plugin tries:

1. `locale/de-DE/<file>.voc`
2. `locale/de/<file>.voc` (language prefix without region)
3. `locale/en-US/<file>.voc` (hard fallback)

Locale folder names use canonical BCP-47 casing (e.g. `en-US`, `de-DE`, `pt-BR`). The `lang` value passed by `OVOSSkill.ask_selection` comes from `self.lang`, which is already normalized by `standardize_lang_tag` and matches this casing. — `ovos_workshop/skills/ovos.py:2035`

Results are cached per language tag in memory (`lru_cache`) so file I/O only happens once per process.

---

## Adding a new language

1. Create the directory using canonical BCP-47 casing (language subtag lowercase, region subtag uppercase):
   ```bash
   mkdir locale/xx-XX
   ```

2. Copy English as a starting point:
   ```bash
   cp locale/en-US/* locale/xx-XX/
   ```

3. Translate every line in every file. Keep one entry per line.

4. **`last.voc`** — include all common words and inflected forms meaning "last", "final", or "latest" in the target language.

5. **Ordinal files** (`first.voc` … `tenth.voc`) — include:
   - The ordinal word(s) in all grammatical forms (gender, case, etc.)
   - Multi-word phrases: `"<ordinal> one"`, `"number <cardinal>"`, `"option <cardinal>"` translated naturally.

   Example `de-DE/second.voc`:
   ```
   zweite
   zweiten
   zweitem
   zweiter
   zweites
   zweite option
   nummer zwei
   ```

6. **Cardinal files** (`one.voc` … `ten.voc`) — include the number word in all forms. These are merged with the ordinal file for the same position.

7. Submit a PR or contribute via [OVOS GitLocalize](https://gitlocalize.com/openvoiceos).

---

## Improving an existing language

Open the relevant `locale/<lang>/` files and add missing:
- Inflected forms (plurals, gendered variants, case endings)
- Regional variants (e.g. `pt-BR` vs `pt-PT`)
- Multi-word phrases for ordinal files if not yet present

Run the tests after editing to verify nothing regresses:

```bash
uv run pytest test/ -v
```

---

## Translation rules

| Rule | Detail |
|------|--------|
| One entry per line | No commas, semicolons, or pipes |
| Lowercase only | The plugin lowercases the utterance before matching |
| No diacritics stripping | Include the exact Unicode form users would say |
| Filenames unchanged | Always `first.voc`, `one.voc`, etc. — never translate the filename |
| Multi-word entries encouraged | Include natural phrases like "second one", "option two" — they prevent false positives from short cardinals |
