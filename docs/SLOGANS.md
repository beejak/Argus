# Repository slogans (rotating tagline)

The blockquote directly under **`# LLM Scanner`** in the root [`README.md`](../README.md) is **auto-rotated** on a schedule so the repo stays lively without repeating until the full pool is exhausted (then it cycles again in the same order).

## Source of truth

| File | Role |
| ---- | ---- |
| [`docs/slogans.json`](../docs/slogans.json) | Ordered pool of unique one-liners (edit here to add more — keep them distinct). |
| [`.github/data/slogan_state.json`](../.github/data/slogan_state.json) | Machine index for the **next** slogan to apply on the next rotation run. |
| [`scripts/rotate_readme_slogan.py`](../scripts/rotate_readme_slogan.py) | Updates the `<!-- SLOGAN_START -->` … `<!-- SLOGAN_END -->` region in `README.md` (centered `<p><i>…</i></p>` HTML so it reads cleanly on GitHub) and advances the index. |

## Automation

Workflow: [`.github/workflows/rotate-slogan.yml`](../.github/workflows/rotate-slogan.yml) (scheduled + manual dispatch). Commits use **`[skip ci]`** so the rotation does not re-trigger the full test matrix.

## Local dry run

```bash
make install   # if needed
make slogan-dry-run
```

## Adding a new line

1. Append a **new** string to the `"slogans"` array in `docs/slogans.json` (no duplicates).  
2. Optionally run `python scripts/rotate_readme_slogan.py --dry-run` to sanity-check parsing.  
3. Merge to `main`; the bot will keep rotating through the longer pool.
