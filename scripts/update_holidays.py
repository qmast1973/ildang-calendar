#!/usr/bin/env python3
"""한국 공휴일(임시공휴일·대체공휴일 포함)을 holidays.json 으로 저장한다.

python-holidays 라이브러리는 법 개정·임시공휴일이 생기면 업데이트되므로,
이 스크립트를 정기적으로(GitHub Actions) 최신 버전으로 실행해 앱이 읽을 파일을 갱신한다.
사용: pip install --upgrade holidays && python scripts/update_holidays.py
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import holidays

OUT = Path(__file__).resolve().parent.parent / "holidays.json"


def clean(name: str) -> str:
    parts = []
    for raw in name.split(";"):
        n = raw.strip()
        if "대체" in n:
            n = "대체공휴일"
        elif "전날" in n or "다음날" in n:
            n = re.sub(r"\s*(전날|다음날)", " 연휴", n)
        elif n == "신정연휴":
            n = "신정"
        elif n == "기독탄신일":
            n = "성탄절"
        if n and n not in parts:
            parts.append(n)
    return "·".join(parts)


def main() -> int:
    this_year = date.today().year
    years = list(range(this_year - 2, this_year + 4))
    kr = holidays.country_holidays("KR", years=years, language="ko")
    result: dict[str, dict[str, str]] = {str(y): {} for y in years}
    for d, name in sorted(kr.items()):
        result[str(d.year)][d.isoformat()] = clean(name)
    payload = {"source": f"python-holidays {holidays.__version__}", "years": result}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"saved {OUT} ({sum(len(v) for v in result.values())} days, {years[0]}-{years[-1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
