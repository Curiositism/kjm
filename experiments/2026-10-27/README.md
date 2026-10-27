# 2026-10-27 스팀 히트펌프 스냅샷 분석

350kW급 160°C 스팀 히트펌프(R1336mzz(Z)) 통합 모니터링 화면 스냅샷 6장과 설계 목표 사이클 화면을 분석한 자료입니다.

- 실험일지(문서): https://claude.ai/artifact/JKdZ7ttdEjdADRkpH8oCvN
- 시각: 사진 EXIF 기준(KST). 화면 Save Time(11:12)은 모든 사진에서 같아서 사용하지 않음.

| 파일 | 내용 |
| --- | --- |
| photos/1137_design_target_cycle.jpg | 설계 목표 사이클 시뮬레이션 화면 (11:37:28) |
| photos/1139_snapshot1_monitor.jpg | 스냅샷 1 (11:39:53) |
| photos/1150_snapshot2_monitor.jpg | 스냅샷 2 (11:50:04) |
| photos/1157_snapshot3_monitor.jpg | 스냅샷 3 (11:57:40) |
| photos/1207_snapshot4_monitor.jpg | 스냅샷 4 (12:07:12) |
| photos/1213_snapshot5_monitor.jpg | 스냅샷 5 (12:13:37) |
| photos/1216_snapshot6_monitor.jpg | 스냅샷 6 (12:16:05) |
| data/snapshot{1..6}.json | 화면 판독값 (T: °C, P: bar.g, 유량 kg/s, 밀도 g/mL, V610 m³/h) |
| figures/ph_snapshot{1..6}_ihx.png | 스냅샷별 P-h 선도 (IHX 입출구 표시) |
| figures/ph_snapshots_vs_design.png | 스냅샷 1~6과 설계 목표 비교 |
| scripts/ | 분석 스크립트 (CoolProp 8.0.0, matplotlib) |

## 재현

```
cd scripts
python3 -I cycle_report.py ../data/snapshot1.json out.png   # 스킬 기본 리포트
python3 -I extra_all.py ../data/snapshot1.json               # 민감도·교차검증
python3 ph_ihx_gen.py ../data/snapshot1.json ph1.png "snapshot 1"
```

`ph_cmp.py`와 `design.py`는 스크래치 경로(`run/…`)를 기준으로 작성돼 있어 실행 전 경로 수정이 필요합니다.

가정: 절대압 = bar.g + 1.01325 bar(표준 대기압).

사용하지 않는 채널: 21(미연결), 604, 606, 607(파란 보조박스 포함). IHX 저압 입구 압력은 P602, IHX 저압 출구 압력은 P507을 쓴다.
