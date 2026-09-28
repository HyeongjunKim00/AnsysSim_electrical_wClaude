"""AEDT / PyAEDT 환경 확인 스크립트.

설치된 PyAEDT 버전과 감지된 AEDT 설치 경로를 출력한다.
    python scripts/common/check_env.py
"""

import sys


def main() -> int:
    try:
        import pyaedt
    except ImportError:
        print("[X] pyaedt 미설치.  ->  pip install pyaedt")
        return 1

    print(f"[OK] pyaedt {pyaedt.__version__}")

    # 설치된 AEDT 버전 탐지
    try:
        from pyaedt.generic.general_methods import installed_versions

        versions = installed_versions()
        if versions:
            print("[OK] 감지된 AEDT 설치:")
            for name, path in versions.items():
                print(f"     - {name}: {path}")
        else:
            print("[!] AEDT 설치를 못 찾음 (라이선스/설치 경로 확인 필요)")
    except Exception as exc:  # noqa: BLE001
        print(f"[!] AEDT 버전 탐지 중 오류: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
