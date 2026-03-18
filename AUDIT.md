# AUDIT — ovos-reranker-fuzzy-plugin

## Known Issues

### ISSUE-001: `lang` parameter ignored in `rerank`
- **File**: `ovos_reranker_fuzzy/__init__.py:29`
- **Severity**: Low
- **Detail**: `rerank` accepts `lang` but does not use it. `rapidfuzz` is language-agnostic; locale-aware tokenization would require additional logic.
- **Mitigation**: Document clearly in FAQ and docstring. Future enhancement if needed.

### ISSUE-002: `voc_match` not available outside OVOSSkill
- **File**: `ovos_workshop/skills/ovos.py:98` (reference)
- **Severity**: Low
- **Detail**: The original `_fuzzy_select` used `voc_match_fn(resp, 'last')` for last-word detection. This plugin uses a hardcoded set `{"last", "latest", "final"}` since `voc_match` is a skill-bound method. Vocabulary files are not accessible here.
- **Mitigation**: The hardcoded set covers the primary English use cases. Non-English last-word detection is not supported.

### ISSUE-003: No CI/CD workflows present
- **Severity**: Medium
- **Detail**: No `.github/workflows/` directory. Standard OVOS workflows (`test.yml`, `build-tests.yml`, `lint.yml`, etc.) are missing.
- **Mitigation**: Add workflows from `OpenVoiceOS/gh-automations@dev` in a follow-up PR.

## Technical Debt

- No type stubs for `rapidfuzz`; mypy may flag untyped imports.
- `extract_number` returns `float`; cast to `int` with `int(num) - 1` is safe for ordinals ≤ options count but not validated for edge cases like `num = 0.5`.
