# Publish to [beejak/Argus](https://github.com/beejak/Argus)

The GitHub repo is the **canonical remote** for this monorepo. The empty upstream was prepared as [`origin`](https://github.com/beejak/Argus.git).

## One-time: authenticate GitHub from WSL

Use either:

- **SSH:** add `git@github.com:beejak/Argus.git` as `origin` and ensure `ssh -T git@github.com` works, or  
- **HTTPS + credential helper / PAT** for `https://github.com/beejak/Argus.git`

## Push `main` (after `make agent-verify` is green)

```bash
cd "/root/LLM Scanner"
make agent-verify
test "$(cat .agent/pytest-last.exit)" -eq 0
git status
git push -u origin main
```

If GitHub still shows the default empty `README` branch, you may need **`git push -u origin main --force`** only if you intentionally replace remote history (usually **not** on first push).

## After first push

- Enable **GitHub Actions** for the repo; workflow: [`.github/workflows/llm-scanner.yml`](../.github/workflows/llm-scanner.yml).  
- Confirm **Actions** tab shows green on `main`.  
- Optional: set default branch to **`main`** in repo Settings if GitHub created `master` elsewhere.

## Cursor plan files

Design plans that lived only under Cursor’s `*.plan.md` should be **summarized** in [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) (already mirrored in-repo); do not rely on IDE-local paths for team onboarding.
