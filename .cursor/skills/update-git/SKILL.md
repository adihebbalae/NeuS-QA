---
name: update-git
description: Sync TimeLogic project work to GitHub — code, session logs, RESULTS.md, and reference docs. Use when the user says "update git", "sync git", or "push updates".
disable-model-invocation: true
---

# Update Git

## Meaning

When the user says **"update git"**, sync **everything that belongs in the repo** so GitHub reflects current work:

1. **Code** — scripts, pipeline glue, config changes that make runs reproducible.
2. **Session logs** — `sessions/YYYY-MM-DD.md` (narrative, decisions, running jobs).
3. **Results ledger** — `RESULTS.md` (scores, submission rows, interpretation).
4. **Reference docs** — `.cursor/rules/` and other repo docs **only when** a future agent or you-at-next-session needs the fact without re-deriving it.

Do **not** treat "update git" as code-only. Do **not** blanket-edit every doc file.

## Decide what needs updating (required step)

Before editing, reason file-by-file: **does this file need a change, or is it already accurate?**

| Signal | Likely update |
|--------|----------------|
| New EvalAI score or submission | `RESULTS.md`, today's session log, `sessions/INDEX.md` headline |
| Run started / stopped / restarted / abandoned | Session log + `RESULTS.md` row; `next-days-plan.md` if that table tracks the run |
| New script or changed launcher behavior | Commit code + one line in session log (what it produces, where outputs live) |
| Strategic pivot (e.g. 1fps → 3fps) | Session **Decisions** + `RESULTS.md` interpretation; skip files that don't reference the run |
| Operational tip for all future agents | `workflow.md` only if it generalizes |
| Stable background (deadline, PI names) | `project-context.md` — **skip** unless something strategic actually changed |

**Skip updates when:**

- The file would only repeat what's already in another canonical place (e.g. duplicating full shard progress in `RESULTS.md` and the session log).
- The change is ephemeral (GPU %, live ETA, per-entry counts) — session log may note *where to monitor*, not live numbers.
- `project-context.md` would get a one-off status line better captured in today's session log.

Prefer **one canonical fact in one place**; cross-link paths instead of copying paragraphs.

## Workflow

1. Inspect repo state:

```bash
git status --short
git diff --stat
git log -3 --oneline
```

2. Apply the table above; list which files you will touch and **why** (briefly, for the user if anything is skipped).

3. Make **focused** edits. Keep raw artifacts out of git unless explicitly requested:

- No `/mnt/Data/...` outputs, logs, submissions, videos, checkpoints, `.venv`, keys.

4. Validate when relevant:

- Lints on changed code.
- Submission JSON: row count, unique IDs, answer format, annotation order.

5. Commit and push:

```bash
git add <relevant files>
git commit -m "$(cat <<'EOF'
<concise message>

EOF
)"
git push origin <current-branch>
git status --short
```

If there is nothing to commit after doc review, say so explicitly (do not empty-commit).

## Commit style

Match repo conventions:

- `docs(sessions): log Sub #5B 3fps restart`
- `docs(results): add Sub #4 tiebreaker score`
- `feat(scripts): add routed submission builder`
- `docs(skills): clarify update-git includes session logs`

## Do not commit

- API keys or `.env`
- Large outputs under `/mnt/Data/...` or `timelogic-data/outputs/`
- Model weights, videos, tmux logs, caches

## Final response

Report:

- Commit hash and branch pushed (or "nothing to commit")
- Files updated and **why each was touched**
- Files **intentionally skipped** and why
- Artifact paths documented but not committed
