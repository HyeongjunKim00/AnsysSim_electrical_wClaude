# 작업 흐름

## 1. 프로젝트 시작
1. `projects/_template`를 복사해 `projects/<이름>` 생성
2. `notes/README.md`에 목적·조건·목표 지표 적기
3. 설계 파일을 `design/`에 저장

## 2. 시뮬레이션 (수동 또는 PyAEDT)
- **수동**: AEDT GUI에서 작업 후 결과를 `results/`로 export
- **자동(PyAEDT)**: `scripts/`의 스크립트로 파라미터 스윕 / 배치 실행
  - 공용 스크립트는 `scripts/<도구>/`
  - 프로젝트 전용은 `projects/<이름>/scripts/`

## 3. 결과 정리
- 수치 결과(CSV, S-param, 온도) → `results/`
- 핵심 그래프/요약 → `results/summary.md` (이건 git에 올라감)

## 도구별 메모
| 도구 | 대상 | 주요 결과물 |
|------|------|-------------|
| HFSS | RF 전자기 (S-param, 안테나, 신호무결성) | `.s*p`, far-field |
| Icepak | 열유동 (온도, 유속) | 온도맵, CSV |
| SIwave | PCB/패키지 SI·PI | S-param, IR drop, Z-param |

## git 커밋 기준
- 커밋할 것: 스크립트, 설정, 노트, 결과 요약(`.md`)
- 커밋 안 할 것: 솔루션 결과 폴더, 대용량 export (`.gitignore` 참고)
