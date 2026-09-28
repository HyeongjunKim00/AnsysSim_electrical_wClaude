# EHD 인쇄 수동소자 — HFSS 시뮬레이션 결과 요약

실행: AEDT 2026 R1 (v261), 배치 모드(`-ng -RunScriptAndExit`), 2026-09-28/29.
스크립트: `../scripts/HFSS_EHD_MIM_capacitor.py`, `../scripts/HFSS_EHD_spiral_inductor.py`

## MIM 커패시터 — ✅ PASS

- 구조: 하부전극/유전막(ALD Al₂O₃ 50nm, εr=9)/상부전극, 전극 60×60 µm, CPW 신호선 삽입
- 목표: 용량밀도 0.1–10 µF/cm²
- **결과: 0.177 µF/cm²** (analytic C=5.737 pF, C@0.5GHz=6.370 pF)
- SRF = 8.36 GHz, Q@1GHz=10.8, Q@5GHz=1.2
- 원본: `MIM_cap_results.txt`, `MIM_cap.s2p`

## 스파이럴 인덕터 (2층, ALD ILD) — ✅ PASS (S11 기준), ⚠️ 용도 제약 있음

- 구조: 외곽 600 µm, 2.5턴, 선폭 50/간격 30 µm, ILD 100nm(ALD Al₂O₃, εr=9), 언더패스 20 µm
- 목표: S11 ≤ -12 dB (0.1–20 GHz 스윕 중 어디서든)
- **결과: best S11 = -15.96 dB @ 6.88 GHz → PASS**
- **주의**: SRF = 3.08 GHz, Q < 1 전 대역 (1GHz: Q=0.42, 2GHz: Q=0.50, 5GHz: Q=-0.49 — 이미 SRF 초과, 용량성 동작).
  S11이 좋게 나온 지점(6.88GHz)은 공진 근처에서 우연히 50Ω에 근접한 것으로, 그 주파수에서 순수 인덕터로 동작하지 않음.
  **3GHz 이하 용도로만 유효.** 더 높은 SRF/Q가 필요하면 언더패스 폭 축소, ILD 두께 증가, 또는 단일층 미앤더 구조 검토 필요.
- 원본: `spiral_ind_results.txt`, `spiral_ind.s2p`

## 재현
```
"C:\Program Files\ANSYS Inc\v261\AnsysEM\ansysedt.exe" -ng -RunScriptAndExit "<script>.py"
```
파라미터는 각 스크립트 상단 "edit here" 섹션에서 수정.
