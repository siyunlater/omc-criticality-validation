"""results.csv를 읽어 계산 keff와 벤치마크 keff를 비교한다."""
import csv
from math import sqrt


def compare(csv_path="results.csv"):
    """각 케이스의 차이(pcm)와 σ 수를 계산해 dict 리스트로 돌려준다.

    diff_pcm = (계산 - 벤치마크) × 1e5
    sigma_pcm = sqrt(계산σ² + 벤치마크σ²) × 1e5   (벤치마크 σ가 비면 0으로 취급)
    n_sigma = diff_pcm / sigma_pcm
    벤치마크 keff가 비어 있으면 diff_pcm 등은 None (원문 확인 대기).
    """
    out = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            keff, sig = float(r["keff"]), float(r["sigma"])
            row = {"case": r["case"], "keff": keff, "sigma": sig,
                   "benchmark_keff": None, "diff_pcm": None,
                   "sigma_pcm": None, "n_sigma": None}
            if r["benchmark_keff"]:
                bk = float(r["benchmark_keff"])
                bs = float(r["benchmark_sigma"] or 0)
                diff = (keff - bk) * 1e5
                s = sqrt(sig**2 + bs**2) * 1e5
                row.update(benchmark_keff=bk, diff_pcm=diff, sigma_pcm=s,
                           n_sigma=diff / s if s else None)
            out.append(row)
    return out


def print_table(rows):
    print(f"{'case':32} {'keff':>8} {'±σ':>8} {'bench':>8} {'Δ(pcm)':>8} {'n_σ':>6}")
    for r in rows:
        if r["diff_pcm"] is None:
            tail = "원문 확인 대기"
        else:
            tail = (f"{r['benchmark_keff']:8.5f} {r['diff_pcm']:+8.0f} "
                    f"{r['n_sigma']:+6.1f}")
        print(f"{r['case']:32} {r['keff']:8.5f} {r['sigma']:8.5f} {tail}")


def to_markdown(rows):
    """compare() 결과를 노트의 '결과' 표와 같은 열 구성의 마크다운 표로 만든다."""
    lines = ["| 케이스 | 벤치마크 keff | OpenMC keff ± σ | 차이 (pcm) | σ 수 |",
             "|---|---|---|---|---|"]
    for r in rows:
        calc = f"{r['keff']:.5f} ± {r['sigma']:.5f}"
        if r["diff_pcm"] is None:
            bench, diff, ns = "(원문 확인 대기)", "-", "-"
        else:
            bench = f"{r['benchmark_keff']:.5f}"
            diff = f"{r['diff_pcm']:+.0f} ± {r['sigma_pcm']:.0f}"
            ns = f"{r['n_sigma']:+.1f}"
        lines.append(f"| {r['case']} | {bench} | {calc} | {diff} | {ns} |")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    args = [a for a in sys.argv[1:] if a != "--md"]
    rows = compare(*args[:1])
    if "--md" in sys.argv:
        print(to_markdown(rows))
    else:
        print_table(rows)
