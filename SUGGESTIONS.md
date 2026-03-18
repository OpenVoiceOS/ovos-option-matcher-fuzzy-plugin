# SUGGESTIONS — ovos-reranker-fuzzy-plugin

## SUG-001: Add locale-aware last-word vocabulary
- Use `ovos-lingua-franca` or a per-lang vocab file to detect "last"/"final" equivalents in non-English languages.
- Priority: Medium — impacts multilingual OVOS deployments.

## SUG-002: Add GitHub Actions CI workflows
- Add standard OVOS workflows: `test.yml`, `build-tests.yml`, `lint.yml`, `license-check.yml`, `pip-audit.yml`, `publish-alpha.yml`, `publish-stable.yml` from `OpenVoiceOS/gh-automations@dev`.
- Priority: High — required for all OVOS repos.

## SUG-003: Expose `rerank` scores in `select_answer`
- Return the top score alongside the selected option (e.g., as a named tuple or dataclass) to allow callers to make secondary confidence decisions.
- Priority: Low — API extension, requires upstream `ReRankerEngine` changes.

## SUG-004: Batch rerank support
- Add a `rerank_batch(queries, options)` method for ranking multiple queries at once using `cdist` matrix, avoiding per-query overhead.
- Priority: Low — useful for pipeline optimization.
