"""keff 결과를 results.csv에 저장하는 함수."""
import csv
from datetime import date
from pathlib import Path

import openmc

from benchmarks import BENCHMARKS

FIELDS = [
    "date", "case", "keff", "sigma",
    "benchmark_keff", "benchmark_sigma",
    "batches", "inactive", "particles", "library",
]


def save_result(case, statepoint, csv_path="results.csv",
                benchmark_keff=None, benchmark_sigma=None, library="ENDF/B-VIII.1"):
    """statepoint 파일에서 keff ± σ를 읽어 csv에 한 줄 추가한다.

    case는 벤치마크 ID (예: "HEU-MET-FAST-001"). benchmarks.py의 BENCHMARKS에
    있으면 기준값을 자동으로 채운다. 인자로 직접 넘기면 그 값이 우선한다.
    BENCHMARKS에도 없고 인자도 없으면 빈 칸 (compare가 "원문 확인 대기"로 표시).
    같은 case가 이미 있으면 새 줄을 추가하지 않고 그 줄을 덮어쓴다.
    """
    if benchmark_keff is None and case in BENCHMARKS:
        benchmark_keff, benchmark_sigma = BENCHMARKS[case]

    with openmc.StatePoint(statepoint) as sp:
        keff = sp.keff
        row = {
            "date": date.today().isoformat(),
            "case": case,
            "keff": f"{keff.nominal_value:.5f}",
            "sigma": f"{keff.std_dev:.5f}",
            "benchmark_keff": "" if benchmark_keff is None else benchmark_keff,
            "benchmark_sigma": "" if benchmark_sigma is None else benchmark_sigma,
            "batches": sp.n_batches,
            "inactive": sp.n_inactive,
            "particles": sp.n_particles,
            "library": library,
        }

    path = Path(csv_path)
    rows = []
    if path.exists():
        with open(path, newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["case"] != case]
    rows.append(row)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return row


if __name__ == "__main__":
    import sys
    # 사용법: python3 results_io.py 벤치마크ID statepoint.200.h5
    print(save_result(sys.argv[1], sys.argv[2]))
