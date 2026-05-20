# Daily session logs

One markdown file per working day at `sessions/YYYY-MM-DD.md`. Written in first person, like an intern's daily journal.

**Where this lives**: `sessions/` at the root of the `adihebbalae/NeuS-QA` fork. NOT under `.cursor/rules/` — session logs would otherwise be injected into every agent prompt, which gets expensive fast. Agents discover the logs via `sessions/INDEX.md` (which IS small enough to live as a rule pointer) and read the relevant day's file on demand.

## Why these exist

1. **Daily slide deck updates** — every entry has a `## For the daily slide` section with 2–4 ready-to-paste bullets.
2. **Future-me / resume bullets** — every entry has a `## Resume-line drafts` section with 1–3 accomplishment statements. At end-of-summer, harvest these.
3. **Project context recovery** — when I come back after a weekend or after a vacation, I can re-read the last 2–3 logs and rebuild context in <10 minutes.
4. **Standups / weekly with Minkyu/Harsh** — easy to scroll through the week before any meeting.
5. **Compute accounting** — every entry logs GPU-hours, OpenAI spend, and disk delta so we can answer "how much did this cost?" later.

## Conventions

- **One file per working day.** If a day has multiple chat sessions, fold them into one file with `### Session N (HH:MM–HH:MM)` subheaders if it helps narrative; otherwise the linear list of accomplishments is fine.
- **First person, past tense.** "I cloned X" not "Cloned X" or "We cloned X". Makes it trivially convertible to a resume bullet.
- **Concrete numbers wherever possible.** "Ran the smoke on 5 entries; 4/5 NSVS ok, 2/5 non-empty foi" not "smoke run mostly worked".
- **Link to artifacts** by path (e.g. `/mnt/Data/ah66742/timelogic/outputs/smoke_v4/`), not by copy-paste.
- **Don't dump full logs into the session file.** Reference the path. Keep the session file scannable; ~1 page is the sweet spot.
- **Pre-commit a TODO for tomorrow.** End every entry with `## Tomorrow / open questions` so the next morning is unblocked.
- **Update `INDEX.md`** with a one-line summary when starting a new day's file.

## Start a new day

```bash
cd ~/NeuS-QA/sessions
./new.sh                    # creates YYYY-MM-DD.md from TEMPLATE.md, opens it in $EDITOR
```

Or manually:

```bash
cp TEMPLATE.md $(date +%F).md
```

## Compute snapshot helper

```bash
cd ~/NeuS-QA/sessions
./compute_snapshot.sh >> $(date +%F).md      # appends current GPU/disk/RAM state
```

## Files in this folder

- `README.md` — this file (conventions)
- `INDEX.md` — one-line summary per day (small, lives as a `.cursor/rules` pointer too)
- `TEMPLATE.md` — copy-and-edit for new days
- `new.sh` — wrapper that creates today's file from the template
- `compute_snapshot.sh` — prints GPU/disk/RAM snapshot, append to the day's log
- `YYYY-MM-DD.md` — one per working day
