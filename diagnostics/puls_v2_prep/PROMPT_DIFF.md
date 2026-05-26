# PULS prompt v2 — few-shot additions (`nsvqa/puls/prompts.py`)

Append-only: **Examples 13–16** added after Example 12. Examples 1–12 unchanged.

Sources: Bucket A/B row patterns in `diagnostics/puls_unknown_analysis/overnight_review.md` (94 empty-PULS + 54 operator-collapse rows from Diagnostic 2).

---

## Bucket A — atemporal MC (empty PULS output)

**Representative row:** QID with stem *"What does the person do in the video?"* (overnight Bucket A; 94 rows dominated by this template family).

| | |
|---|---|
| **Before (no matching few-shot)** | Model returns empty JSON — no `proposition`, no `specification` → NSVS bypass / `unknown` family. |
| **After (Example 14)** | Generic query action, not grounding a specific option: |

**Input (verbatim MC wrapper):**
```
The following is a multiple choice question with four possible answer choices: A, B, C, D. What does the person do in the video ? Is it Option A: hold a dish, Option B: open a door, Option C: sit in a chair, Option D: wash a table. Reply with the chosen option in one character.
```

**Output:**
```json
{
  "proposition": ["person performs action in video"],
  "specification": "(person performs action in video)"
}
```

**Example 13** covers the sibling stem *"What action does the person do throughout the video?"* (e.g. overnight QID with options watch/close/open book, wash table) with the same generic proposition/spec.

---

## Bucket B — co-occurrence / non-overlap (operator collapse)

**Representative rows:** QID 932 (co-occurrence), QID 1085 (non-overlap) in overnight Bucket B.

| | |
|---|---|
| **Before (collapse)** | Single anchor prop only, e.g. QID 932: `propositions: ['holding_a_bag']`, `spec: ("holding_a_bag")` — relational structure dropped. |
| **After (Examples 15–16)** | Anchor **and** candidate slot so NSVS can score options against the relation. |

**Co-occurrence — Example 15 (from QID 932 stem):**

Input:
```
... Which action always co-occurs with holding a bag ? Is it Option A: hold some food, ...
```

Output:
```json
{
  "proposition": ["person holds a bag", "person performs candidate action"],
  "specification": "person holds a bag AND person performs candidate action"
}
```

**Non-overlap — Example 16 (from QID 1085 stem):**

Input:
```
... Which action by the person does not overlap with adding coffee ? Is it Option A: pour milk, ...
```

Output:
```json
{
  "proposition": ["person adds coffee", "person performs candidate action"],
  "specification": "NOT (person adds coffee AND person performs candidate action)"
}
```

---

## Regression check — unchanged example

**Example 1** (pre-existing) is untouched:

Input: `"In a sunny meadow, a child plays with a kite and runs around. What does the child do after falling?"`

Output:
```json
{
  "proposition": ["child plays with kite", "child runs around", "child falls"],
  "specification": "(child plays with kite AND child runs around) UNTIL child falls"
}
```

No edits to Examples 1–12 text or ordering.
