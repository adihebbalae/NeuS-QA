# Failure-audit artifacts (tracked copies)

Human-readable disagreement audit packets for Sub #1 vs Sub #5B. Canonical working copies also live on disk at `/mnt/Data/ah66742/timelogic/outputs/diagnostics/`.

| Version | Repo path | Builder | Notes |
| --- | --- | --- | --- |
| v1 | [sub5b_failure_audit_v1/](sub5b_failure_audit_v1/) | `scripts/build_failure_audit_packet.py` | 25 rows; 5 percentiles + FOI midpoint; duration-stratified |
| v2 | [sub5b_failure_audit_v2/](sub5b_failure_audit_v2/) | same | Dense frames on short clips, frame dedupe, video `file://` links, aligned caption labels |

Compare CSV/summary: `/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub1_vs_sub5b_fix2/` (464 disagreements, 76.8% agree).

**How to read:** rows are **disagreements**, not “Sub #5B wrong.” No local GT — spot-check star/agqa at **0.25× playback** (time-warped clips).
