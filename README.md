# OpenMC criticality validation (ICSBEP benchmarks)

Small Python tooling to run criticality benchmarks with [OpenMC](https://openmc.org)
(ENDF/B-VIII.1) and compare the calculated k-eff with the published reference values:
difference in pcm, number of combined standard deviations, table and plot.

## Results (200-1000 batches x 10,000 particles, ENDF/B-VIII.1)

| Benchmark | Description | k-eff (OpenMC) | Reference | Diff. (pcm) | n_sigma |
|---|---|---|---|---|---|
| PU-MET-FAST-001 | Bare Pu sphere (Jezebel) | 0.99907 +/- 0.00046 | 1.0000 +/- 0.0020 | -93 | -0.5 |
| HEU-MET-FAST-001 | Bare HEU sphere (Godiva) | 0.99986 +/- 0.00047 | 1.0000 +/- 0.0010 | -14 | -0.1 |
| U233-MET-FAST-001 | Bare U-233 sphere | 0.99946 +/- 0.00047 | 1.0000 +/- 0.0010 | -54 | -0.5 |
| MIX-MET-FAST-001 | Pu sphere in HEU shell (Planet) | 0.99856 +/- 0.00048 | 1.0000 +/- 0.0016 | -144 | -0.9 |
| PU-MET-FAST-006 | Pu sphere, natural U reflector (Flattop-Pu) | 0.99961 +/- 0.00061 | 1.0000 +/- 0.0030 | -39 | -0.1 |
| HEU-SOL-THERM-032 | Uranyl nitrate solution sphere, Al vessel | 0.99870 +/- 0.00026 | 1.0015 +/- 0.0026 | -280 | -1.1 |

## Layout

| File | Role |
|---|---|
| `run_all.py` | run every case, save results, print the comparison table (`--skip-run`, `--md`, `--csv`) |
| `results_io.py` | `save_result()`: read k-eff from a statepoint and write one row to `results.csv` |
| `benchmarks.py` | reference k-eff +/- sigma per benchmark ID |
| `compare.py` | difference (pcm), combined sigma, n_sigma, text / markdown table |
| `plot.py` | n_sigma bar chart (PNG) |
| `<case>/` | one input script per benchmark |

```bash
export OPENMC_CROSS_SECTIONS=/path/to/endfb-viii.1-hdf5/cross_sections.xml
python3 run_all.py            # all cases (the solution case takes a few minutes)
python3 run_all.py --skip-run # rebuild table/CSV from existing statepoints
python3 plot.py
```

## Sources and limits (please read)

- **No ICSBEP Handbook content is included**, and I did not have access to the Handbook.
  Reference k-eff values and the geometry/atom densities of the input scripts come from the
  public repository [mit-crpg/benchmarks](https://github.com/mit-crpg/benchmarks)
  (MIT License; reference values from `icsbep/icsbep/uncertainties.csv`). This is therefore a
  comparison against a **secondary source**, not against the Handbook itself.
- The input scripts were rewritten by hand from those models and checked numerically against them
  (atom densities and radii); they are **not independently derived**.
- `n_sigma` combines only the Monte Carlo statistical uncertainty and the benchmark uncertainty
  (in quadrature). Nuclear-data uncertainty and model simplifications are **not** included, so
  `|n_sigma| < 1` does not mean the code/data are accurate. Cases with a large benchmark
  uncertainty (e.g. Flattop-Pu, +/-0.0030) have little power to detect a bias.
- All six differences are negative. With six cases and these uncertainties this cannot be
  attributed to a cause (nuclear data, benchmark definition, model simplification).
- Only one thermal-spectrum case; the rest are fast metal systems.
