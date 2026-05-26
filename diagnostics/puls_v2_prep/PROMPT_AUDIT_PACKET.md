# PULS prompt v2 — quick audit packet (5–10 min skim)

**Purpose:** Review three design choices in Examples 13–16 (`nsvqa/puls/prompts.py`) before any PULS re-run.  
**Related:** `PROMPT_DIFF.md`, overnight rows in `diagnostics/puls_unknown_analysis/overnight_review.md`.  
**No API** — shows post-`process_specification` strings and how NSVS uses them today.

Mark each decision: **Approve** / **Change to alt** / **Block**.

---

## How to use this doc

1. Read the **Decision** box for A → B → C (in order).
2. Glance **Downstream trace** — what NSVS actually runs.
3. Use **Spot-check QIDs** if you want a real val row in `overnight_review.md`.
4. Note decisions at the bottom **Sign-off** table.

---

## A — Bucket A hook: `person performs action in video`

**Failure we're fixing:** 94 val rows, `empty_puls_output` — PULS returns no JSON → NSVS never runs → FOI `[-1]` (Diagnostic 2).

**Question type:** Atemporal MC — *"What does the person do in the video?"* / *"…throughout the video?"* with four action labels. We must **not** pick one option in PULS; VQA still sees all four options later.

### Phrase options (pick one)

| Option | PULS proposition (natural) | After `process_specification` | NSVS VLM question (per window) |
|--------|---------------------------|--------------------------------|--------------------------------|
| **A1 (current, Ex. 13–14)** | `person performs action in video` | `person_performs_action_in_video` | `Is there a 'person performs action in video' present…?` |
| **A2 (richer, still generic)** | `person performs main action in video` | `person_performs_main_action_in_video` | Same pattern, adds "main" |
| **A3 (verb-forward)** | `person performs visible action` | `person_performs_visible_action` | Same pattern, stresses visibility |

### Downstream trace (A1)

```
PULS JSON → process_specification → props: ["person_performs_action_in_video"]
                                  → spec:  ("person_performs_action_in_video")
→ Storm wrapper: P>=0.60 [ ("person_performs_action_in_video") ]
→ Per 3-frame window: one VLM yes/no on the generic phrase (not per MC option)
→ FOI from automaton ∩ detection windows (may still be [-1] if detect fails — different lever)
```

**Diagnostic 2 gate:** `is_groundable_prop` — passes via `person_` prefix (`scripts/analyze_puls_unknown_bypassed.py`). Not blocked as `no_groundable_propositions`.

**What this does *not* fix:** Does not tell NSVS which of A/B/C/D is correct; only avoids total PULS empty bypass. MC disambiguation stays in **GPT VQA** on crop + full question text.

### Spot-check QIDs (Bucket A)

| QID | Stem (short) | Overnight PULS |
|-----|----------------|----------------|
| (many) | `What action does the person do throughout the video ?` | EMPTY |
| — | `What does the person do in the video ?` (Ex. 14) | EMPTY |

### Decision A

- [ ] **Approve A1** — generic hook is enough; goal is non-empty spec + one detectable prop.
- [ ] **Change to A2 or A3** — specify which phrase in a comment on Ex. 13–14.
- [ ] **Block** — need different structure (e.g. multi-prop); describe: _______________

**Risk to note:** Very generic prop → noisy yes/no across whole video; acceptable trade vs 100% bypass today?

---

## B — Bucket B non-overlap: `NOT (anchor AND candidate)` vs `NOT anchor`

**Failure we're fixing:** 54 rows, `operator_collapse_open_ended` / `relation_not_in_spec` — e.g. only `("person_adds_coffee")` with no relational structure (QID **1085** in overnight doc).

**Question type:** *"Which action does not overlap with adding coffee?"* — MC asks which **option** fails to overlap with anchor X.

### Spec options (Example 16 anchor = adding coffee)

| Option | PULS spec (natural) | After `process_specification` | Storm LTL (threshold 0.6) |
|--------|---------------------|-------------------------------|---------------------------|
| **B1 (current, Ex. 16)** | `NOT (person adds coffee AND person performs candidate action)` | `!("person_adds_coffee" & "person_performs_candidate_action")` | `P>=0.60 [ !("person_adds_coffee" & "person_performs_candidate_action") ]` |
| **B2 (reject for MC)** | `NOT person adds coffee` | `!"person_adds_coffee"` | `P>=0.60 [ !"person_adds_coffee" ]` |
| **B3 (co-occurrence only, Ex. 15)** | `person holds a bag AND person performs candidate action` | `"person_holds_a_bag" & "person_performs_candidate_action"` | `P>=0.60 [ "person_holds_a_bag" & "person_performs_candidate_action" ]` |

### Why Diagnostic 2 cares (not full TL semantics)

Auto-classifier rule (`analyze_puls_unknown_bypassed.py`):

- Questions matching `co-occur|overlap|always occur` need **`len(props) >= 2`** and **`&` or ` U `** in spec.
- Old collapse: 1 prop, spec `("person_adds_coffee")` → **`relation_not_in_spec`** or **`operator_collapse_open_ended`**.
- **B1** satisfies the structural gate; **B2** still has 1 prop if you drop candidate → fails gate again.

### Semantics sketch (informal — no GT here)

| Frame situation | B1 `!(A & B)` high? | B2 `!A` high? |
|-----------------|---------------------|---------------|
| Coffee yes, generic candidate yes | Low (both true → negated) | Low |
| Coffee yes, candidate no | High | Low (coffee still seen) |
| Coffee no | High | High |

**B2** treats “no coffee anywhere” like success — wrong shape for *“which option doesn’t overlap with coffee”* (coffee is usually present; question is about **other** actions vs coffee interval).

**B1** requires **both** prop detections in the same model-check step for the conjunction inside `NOT (...)` — coarser than per-option overlap, but encodes a **binary relation** Storm can score.

**UNTIL split:** Specs with **no** ` U ` put all props in split 0 (`PropertyChecker.check_split`). Both props share one detection bucket for FOI intersection logic.

### Spot-check QIDs (Bucket B)

| QID | Type | Old PULS (collapsed) | v2 target (Ex.) |
|-----|------|----------------------|-----------------|
| **932** | co-occurs + holding a bag | `("holding_a_bag")` | Ex. **15** (AND) |
| **1085** | does not overlap + adding coffee | (similar single-prop) | Ex. **16** (NOT AND) |
| **359** | does not overlap + putting clothes | `("person_puts_clothes_somewhere")` | Ex. 16 pattern |

### Decision B — co-occurrence (Ex. 15)

- [ ] **Approve B3** — `anchor AND candidate` for co-occurrence MC.
- [ ] **Change** — prefer `UNTIL` or other TL: _______________

### Decision B — non-overlap (Ex. 16)

- [ ] **Approve B1** — `NOT (anchor AND candidate)`.
- [ ] **Change to B2** — understand: likely re-fails Diagnostic 2 structure + weaker MC semantics.
- [ ] **Change** — alternate TL: _______________

---

## C — `person performs candidate action` (MC placeholder)

**Intent:** One **generic** second proposition so PULS does not collapse to anchor-only; **do not** emit four option-specific props in PULS (would bloat spec / break “each proposition exactly once” rule for a single MC question).

### What happens in the stack

| Stage | Behavior |
|-------|----------|
| **PULS** | Always outputs the same second prop string for any co-occurrence / non-overlap MC template. |
| **`process_specification`** | → `person_performs_candidate_action` |
| **NSVS detect** | Same generic prompt every window: `Is there a 'person performs candidate action' present…?` **Not** “hold some food” / “pour milk” per option. |
| **VQA (Sub #5B)** | Still receives **full MC stem + Options A–D** on cropped clip; chooses letter. |

### Tradeoff (explicit)

| Pro | Con |
|-----|-----|
| Passes Diagnostic 2 multi-prop + `&` / `NOT` gates | Does **not** run four parallel NSVS tracks per option |
| Matches “don’t ground a specific option in PULS” for Bucket A | `candidate` is abstract; detect signal may be weak/noisy |
| Keeps prompt size stable | True per-option overlap/co-occurrence needs **future** work (option loop or VQA-only) |

### Alternatives (if placeholder feels too weak)

| Alt | Idea | Cost |
|-----|------|------|
| **C1 (current)** | `person performs candidate action` | 1 extra detect pass; generic |
| **C2** | Use anchor only + `UNTIL` dummy second prop | Hacky; may confuse Storm |
| **C3** | Four props (one per option) + OR in spec | Violates “exactly once” spirit; 4× detect cost |

### Decision C

- [ ] **Approve C1** — placeholder is intentional; structural fix first, option-level NSVS later.
- [ ] **Change** — describe: _______________

---

## Regression sanity (unchanged examples)

| Check | Status |
|-------|--------|
| Examples **1–12** text unmodified | See `PROMPT_DIFF.md` § Regression |
| New examples **append only** after Ex. 12 | `prompts.py` L108–134 |

---

## Sign-off (fill after skim)

| ID | Decision | Notes |
|----|----------|-------|
| A | ☐ Approve A1 ☐ A2 ☐ A3 ☐ Block | |
| B co-occur | ☐ Approve B3 ☐ Change | |
| B non-overlap | ☐ Approve B1 ☐ B2 ☐ Change | |
| C placeholder | ☐ Approve C1 ☐ Change | |

**Reviewer:** _____________ **Date:** _____________

**Next step after approve:** Smoke PULS on 3–5 QIDs per bucket (no full val) → check `puls.proposition` / `puls.specification` in entries + `analyze_puls_unknown_bypassed` category on those QIDs only.
