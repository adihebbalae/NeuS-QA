# Test video duration audit (OpenCV)

Generated: 2026-05-23T23:38:33.842716+00:00

## Probe method

- Backend: **OpenCV** (`cv2.VideoCapture` metadata) — **ffprobe not installed** on this host.
- Admin action needed for canonical container probes: `sudo apt install ffmpeg` (or run this script on a machine with ffprobe and `--probe-backend ffprobe`).
- OpenCV durations matched QID 1809 calibration (`star_1SLTT.mp4`: 14 frames @ 25 fps → 0.56 s) but may diverge from ffprobe on some codecs.

## Scope

- Annotations: `/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json`
- Video root: `/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json`
- Unique test videos referenced: **1850**
- Test question rows referencing those videos: **3000**
- Probed successfully: **1850**
- Missing on disk: **0**
- Probe errors: **0**

## Speed-distortion flags (likely time-warped clips)

Thresholds flag videos where temporal operators (`immediately_after`, `since`, …) may collapse at 1× playback (cf. QID 1809).

| Threshold | Videos | % of probed |
| --- | ---: | ---: |
| `< 2.0 s` | 844 | 45.6% |
| `< 1.0 s` | 424 | 22.9% |
| `< 0.5 s` | 116 | 6.3% |

## By source dataset (`< 2 s` / total probed)

| Source | probed | `< 2 s` | `< 2 s` % |
| --- | ---: | ---: | ---: |
| agqa | 473 | 430 | 90.9% |
| bf | 439 | 0 | 0.0% |
| ct | 472 | 0 | 0.0% |
| star | 466 | 414 | 88.8% |

## Question-row duration buckets (3000 test Q)

Weighted by how many questions hit each video (not unique-video counts).

| Bucket | Question rows | % |
| --- | ---: | ---: |
| `< 2 s` | 1331 | 44.4% |
| `2–10 s` | 206 | 6.9% |
| `10–60 s` | 195 | 6.5% |
| `> 60 s` | 1268 | 42.3% |

| Source | `< 2 s` Q rows / source total |
| --- | ---: |
| agqa | 672 / 760 (88.4%) |
| bf | 0 / 734 (0.0%) |
| ct | 0 / 729 (0.0%) |
| star | 659 / 777 (84.8%) |

Video duration stats (1850 probed): min **0.040 s**, median **2.72 s**, mean **105.8 s**, max **612.4 s**.

## Val vs test (unique videos `< 2 s`)

| Split | Videos `< 2 s` | agqa | star | bf | ct |
| --- | ---: | ---: | ---: | ---: | ---: |
| Val (923 probed) | 51.0% | 85.8% | 82.0% | 0% | 0% |
| Test (1850 probed) | 45.6% | 90.9% | 88.8% | 0% | 0% |

## Shortest probed videos (top 15)

| video_id | duration (s) | fps | frames | question rows |
| --- | ---: | ---: | ---: | ---: |
| agqa_GN912.mp4 | 0.040 | 25.0 | 1 | 1 |
| agqa_77HDM.mp4 | 0.080 | 25.0 | 2 | 1 |
| star_S8TT8.mp4 | 0.120 | 25.0 | 3 | 2 |
| agqa_5NG8W.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_C0207.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_G2WHU.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_KDYNB.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_M5C5L.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_XMINJ.mp4 | 0.160 | 25.0 | 4 | 1 |
| star_A1VTR.mp4 | 0.160 | 25.0 | 4 | 1 |
| star_EHHRS.mp4 | 0.160 | 25.0 | 4 | 1 |
| agqa_0MJHH.mp4 | 0.200 | 25.0 | 5 | 1 |
| agqa_YZWQH.mp4 | 0.200 | 25.0 | 5 | 2 |
| star_5AFC1.mp4 | 0.200 | 25.0 | 5 | 1 |
| star_D548M.mp4 | 0.200 | 25.0 | 5 | 1 |

## Artifacts

- CSV: `video_duration_audit.csv`

