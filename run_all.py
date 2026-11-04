"""모든 케이스를 한 번에 실행 → results.csv 저장 → 비교 표 출력.

사용법
  python3 run_all.py                      # 전체 케이스 실행
  python3 run_all.py HEU-MET-FAST-001     # 지정한 케이스만
  python3 run_all.py --skip-run           # 실행 없이, 이미 있는 statepoint로 csv/표만 갱신
  python3 run_all.py --csv test.csv       # 결과 파일 지정 (시험할 때)
  python3 run_all.py --md                 # 표를 마크다운으로 출력 (노트에 붙일 때)
"""
import argparse
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

from compare import compare, print_table, to_markdown
from results_io import save_result

ROOT = Path(__file__).resolve().parent
DEFAULT_XS = Path.home() / "openmc_data/endfb-viii.1-hdf5/cross_sections.xml"

# 벤치마크 ID: (폴더, 입력 스크립트)
CASES = {
    "PU-MET-FAST-001": ("jezebel_pu", "jezebel_pu.py"),
    "HEU-MET-FAST-001": ("godiva", "godiva.py"),
    "U233-MET-FAST-001": ("jezebel_u", "jezebel_u233.py"),
    "MIX-MET-FAST-001": ("mix", "mix.py"),
    "PU-MET-FAST-006": ("flattop_pu", "flattop_pu.py"),
    "HEU-SOL-THERM-032": ("heu_sol_therm_032", "heu_sol_therm_032.py"),
}


def run_case(case, folder, script, env):
    """스크립트를 실행하고, 이번 실행에서 새로 만들어진 statepoint 경로를 돌려준다."""
    workdir = ROOT / folder
    start = time.time()
    with open(workdir / "run.log", "w") as log:
        proc = subprocess.run([sys.executable, script], cwd=workdir, env=env,
                              stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.time() - start
    if proc.returncode != 0:
        raise RuntimeError(f"Fail: script (termination code: {proc.returncode}), {workdir / 'run.log'} check")
    return latest_statepoint(workdir, newer_than=start), elapsed


def latest_statepoint(workdir, newer_than=None):
    files = glob.glob(str(workdir / "statepoint.*.h5"))
    if not files:
        raise FileNotFoundError(f"No statepoint in {workdir}")
    path = max(files, key=os.path.getmtime)
    # 스크립트가 실패했는데 예전 결과가 남아 있어 그걸 저장하는 사고를 막는다
    if newer_than is not None and os.path.getmtime(path) < newer_than:
        raise RuntimeError("No statepoitn file in this run (old statepoint)")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases", nargs="*", help="Benchmark ID (run all without this)")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--csv", default=str(ROOT / "results.csv"))
    parser.add_argument("--md", action="store_true")
    args = parser.parse_args()

    unknown = [c for c in args.cases if c not in CASES]
    if unknown:
        sys.exit(f"Unknwon case: {unknown}\npossible ID: {list(CASES)}")
    selected = args.cases or list(CASES)

    env = dict(os.environ)
    if not env.get("OPENMC_CROSS_SECTIONS"):
        env["OPENMC_CROSS_SECTIONS"] = str(DEFAULT_XS)

    failures = []
    for case in selected:
        folder, script = CASES[case]
        try:
            if args.skip_run:
                sp, elapsed = latest_statepoint(ROOT / folder), None
            else:
                sp, elapsed = run_case(case, folder, script, env)
            save_result(case, sp, csv_path=args.csv)
            note = "" if elapsed is None else f" ({elapsed:.0f} s)"
            print(f"[ok]   {case}{note}")
        except Exception as e:  # 한 케이스가 실패해도 나머지는 계속
            failures.append((case, e))
            print(f"[실패] {case}: {e}")

    rows = [r for r in compare(args.csv) if r["case"] in selected]
    print()
    if args.md:
        print(to_markdown(rows))
    else:
        print_table(rows)

    if failures:
        print(f"\n실패 {len(failures)}개: {[c for c, _ in failures]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
