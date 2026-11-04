"""results.csv의 n_σ를 막대 그래프(PNG)로 저장한다.

사용법
  python3 plot.py                          # results.csv → n_sigma.png
  python3 plot.py --csv test.csv --out a.png
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 화면이 없는 환경(ubuntu 머신)에서는 파일로만 저장
import matplotlib.pyplot as plt

from compare import compare

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases", nargs="*", help="Benchmark ID (all if omitted)")
    parser.add_argument("--csv", default=str(ROOT / "results.csv"))
    parser.add_argument("--out", default=str(ROOT / "n_sigma.png"))
    args = parser.parse_args()

    # 기준값이 없는 케이스(n_sigma가 None)는 그릴 수 없으므로 뺀다
    rows = [r for r in compare(args.csv)
            if r["n_sigma"] is not None and (not args.cases or r["case"] in args.cases)]
    if not rows:
        raise SystemExit("No case (need results with benchmark)")

    cases = [r["case"] for r in rows]
    n_sigma = [r["n_sigma"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(cases, n_sigma, color="#4C78A8")

    # 기준선: 0, ±1σ, ±2σ
    ax.axhline(0, color="black", linewidth=0.8)
    for y in (-2, -1, 1, 2):
        ax.axhline(y, color="gray", linestyle="--", linewidth=0.7)

    # 막대 옆에 차이(pcm)를 적는다 — n_σ만 보면 기준값 σ가 큰 케이스가 좋아 보이는 착시가 있다
    for bar, r in zip(bars, rows):
        ax.annotate(f"{r['diff_pcm']:+.0f} pcm",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom" if bar.get_height() >= 0 else "top", fontsize=8)

    ax.set_ylim(-3, 3)
    ax.set_ylabel(r"$n_\sigma$ = (calc - benchmark) / combined $\sigma$")
    ax.set_title("OpenMC vs ICSBEP benchmark keff (ENDF/B-VIII.1)")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"save: {args.out}")


if __name__ == "__main__":
    main()
