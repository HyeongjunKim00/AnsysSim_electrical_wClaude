# AnsysSim

Ansys 시뮬레이션 작업 공간. **HFSS**(RF 전자기) · **Icepak**(열유동) · **SIwave**(SI·PI)를
Ansys Electronics Desktop(AEDT)과 PyAEDT(Python 자동화)로 다룬다.

## 폴더 구조

```
AnsysSim/
├── projects/            # 시뮬레이션 프로젝트 (하나당 폴더 하나)
│   └── _template/       # 새 프로젝트 시작용 템플릿 (복사해서 씀)
│       ├── design/      # .aedt / .aedb 원본 설계 파일
│       ├── scripts/     # 이 프로젝트 전용 스크립트
│       ├── results/     # export한 결과 (git 제외 — 대용량)
│       └── notes/       # 설정값, 관찰, 메모
├── scripts/             # 재사용 스크립트 (PyAEDT)
│   ├── hfss/
│   ├── icepak/
│   ├── siwave/
│   └── common/          # 공통 유틸 (연결, export, 재료 로딩 등)
├── lib/
│   └── materials/       # 공용 재료 물성 정의
└── docs/
    └── workflow.md      # 작업 흐름 / 규칙
```

## 새 프로젝트 시작

```powershell
Copy-Item -Recurse projects\_template projects\<프로젝트이름>
```

## PyAEDT 환경 (선택)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pyaedt
python scripts\common\check_env.py   # AEDT 연결 확인
```

## 규칙

- **원본 설계**(`.aedt`, `.aedb`)는 `design/`에만, 결과는 `results/`에만.
- `results/` 대용량 산출물은 git에 안 올라감(`.gitignore`). 요약/플롯 `.md`는 올라감.
- 재현 가능한 것(스크립트·설정)을 버전 관리하고, 재계산되는 것(솔루션)은 제외.
