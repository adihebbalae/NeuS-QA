# Val video duration audit

Generated: 2026-05-23T22:45:39.618579+00:00

## Probe method

- Backend: **OpenCV** (`cv2.VideoCapture` metadata) — **ffprobe not installed** on this host.
- Admin action needed for canonical container probes: `sudo apt install ffmpeg` (or run this script on a machine with ffprobe and `--probe-backend ffprobe`).
- OpenCV durations matched QID 1809 calibration (`star_1SLTT.mp4`: 14 frames @ 25 fps → 0.56 s) but may diverge from ffprobe on some codecs.

## Scope

- Annotations: `/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json`
- Video root: `/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos`
- Unique val videos referenced: **940**
- Val question rows referencing those videos: **2000**
- Probed successfully: **923**
- Missing on disk: **17**
- Probe errors: **0**

## Speed-distortion flags (likely time-warped clips)

Thresholds flag videos where temporal operators (`immediately_after`, `since`, …) may collapse at 1× playback (cf. QID 1809).

| Threshold | Videos | % of probed |
| --- | ---: | ---: |
| `< 2.0 s` | 471 | 51.0% |
| `< 1.0 s` | 177 | 19.2% |
| `< 0.5 s` | 37 | 4.0% |

## By source dataset (`< 2 s` / total probed)

| Source | probed | `< 2 s` | `< 2 s` % |
| --- | ---: | ---: | ---: |
| agqa | 268 | 230 | 85.8% |
| bf | 84 | 0 | 0.0% |
| ct | 277 | 0 | 0.0% |
| star | 294 | 241 | 82.0% |

## Shortest probed videos (top 15)

| video_id | duration (s) | fps | frames | val questions |
| --- | ---: | ---: | ---: | ---: |
| agqa_GI7JM.mp4 | 0.160 | 25.0 | 4 | 1 |
| star_BZWSJ.mp4 | 0.160 | 25.0 | 4 | 1 |
| star_FV9AL.mp4 | 0.160 | 25.0 | 4 | 2 |
| agqa_MQSXF.mp4 | 0.200 | 25.0 | 5 | 2 |
| star_LD8PU.mp4 | 0.200 | 25.0 | 5 | 1 |
| star_QYE21.mp4 | 0.240 | 25.0 | 6 | 1 |
| agqa_79WPY.mp4 | 0.280 | 25.0 | 7 | 1 |
| agqa_MILRI.mp4 | 0.280 | 25.0 | 7 | 1 |
| agqa_T53HV.mp4 | 0.320 | 25.0 | 8 | 1 |
| star_3BH39.mp4 | 0.320 | 25.0 | 8 | 1 |
| star_E33IO.mp4 | 0.320 | 25.0 | 8 | 1 |
| star_LFPLP.mp4 | 0.320 | 25.0 | 8 | 1 |
| star_XRWBL.mp4 | 0.320 | 25.0 | 8 | 1 |
| agqa_7YMK9.mp4 | 0.360 | 25.0 | 9 | 1 |
| agqa_J1EA0.mp4 | 0.360 | 25.0 | 9 | 1 |

## Missing on disk

- `ct_1jqTfi145xQ.mp4`
- `ct_78c2HuuwmVA.mp4`
- `ct_7MWzU--xApU.mp4`
- `ct_BtDvFEFiQ5k.mp4`
- `ct_GbgRRMMJHTU.mp4`
- `ct_I-9uVsmWoEU.mp4`
- `ct_L0MVdMNihGI.mp4`
- `ct_LKd2oIsM3uE.mp4`
- `ct_MEYXUyEXd88.mp4`
- `ct_Mlscv4JxrfU.mp4`
- `ct_Sm-Er9tMi8g.mp4`
- `ct_Uj0WzaLGg3Y.mp4`
- `ct_VEjQ3lIZIb4.mp4`
- `ct_XhZnEq3mJy4.mp4`
- `ct_sBJJ0Cj0GG4.mp4`
- `ct_ygv6jXn59t8.mp4`
- `ct_yyIOce1XvpY.mp4`

## Artifacts

- CSV: `video_duration_audit.csv`

