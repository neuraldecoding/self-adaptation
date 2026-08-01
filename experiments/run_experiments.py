#!/usr/bin/env python3
"""Measure how much each defect A1-A4 contributes to the numbers in Table 2.

Runs the port in experiments/kma_py over the 23 benchmark functions for six
configurations: the published code, each single fix in isolation, and all four
fixes together. Because only the toggled defect differs between a configuration
and `published`, the delta is attributable to that defect.

    python3 run_experiments.py [--seeds 30] [--dim 50] [--jobs 12]

Writes results/raw.csv and results/summary.md.
"""
import argparse
import csv
import os
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

from kma_py.kma import Config, run

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

CONFIGS = [
    Config(),                                       # published
    Config(fix_case14=True),                        # A1
    Config(fix_allhq=True),                         # A2
    Config(fix_mlipir=True),                        # A3
    Config(fix_evalcount=True),                     # A4
    Config(fix_allhq=True, fix_mlipir=True),        # both origin-bias channels
    Config(True, True, True, True),                 # all
]
FUNCTIONS = list(range(1, 24))
# Global optima as printed in Table 6 of the manuscript, for the "reached" check.
PAPER_KMA_AVG = {
    1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 4.831e1, 6: 0.0, 7: 1.715e-4,
    8: -1.701e4, 9: 0.0, 10: 8.882e-16, 11: 0.0, 12: 2.799e-3, 13: 5.270e-2,
    14: 9.980e-1, 15: 3.075e-4, 16: -1.032, 17: 3.979e-1, 18: 3.0,
    19: -3.861, 20: -3.320, 21: -10.1532, 22: -10.4029, 23: -10.5364,
}


def _one(job):
    fid, dim, seed, cfg = job
    r = run(fid, dim, seed, cfg)
    r["seed"] = seed
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--dim", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    jobs = [(fid, args.dim, seed, cfg)
            for cfg in CONFIGS for fid in FUNCTIONS for seed in range(1, args.seeds + 1)]
    print(f"{len(jobs)} runs on {args.jobs} workers ...", flush=True)
    with Pool(args.jobs) as pool:
        rows = pool.map(_one, jobs, chunksize=4)

    os.makedirs(RESULTS, exist_ok=True)
    fields = ["config", "fid", "seed", "reported_best", "true_best", "reached",
              "crashed", "real_evals", "counted_evals", "stage", "gens", "zero_hq_rows"]
    with open(os.path.join(RESULTS, "raw.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})

    agg = defaultdict(list)
    for r in rows:
        agg[(r["config"], r["fid"])].append(r)

    def stat(cfgname, fid):
        rs = agg[(cfgname, fid)]
        crashed = sum(1 for r in rs if r["crashed"])
        vals = [r["true_best"] for r in rs if r["true_best"] is not None]
        if not vals:
            return None
        return dict(n=len(rs), crashed=crashed, avg=float(np.mean(vals)),
                    std=float(np.std(vals, ddof=0)),
                    gua=sum(1 for r in rs if r["reached"]) / len(rs),
                    real=float(np.mean([r["real_evals"] for r in rs])),
                    counted=float(np.mean([r["counted_evals"] for r in rs])),
                    zeros=int(np.max([r["zero_hq_rows"] for r in rs])))

    names = [c.name for c in CONFIGS]
    out = [f"# Hasil eksperimen: kontribusi tiap temuan A1-A4",
           "",
           f"{args.seeds} run independen per sel, dimensi {args.dim} untuk F1-F13, "
           f"anggaran 25.000 evaluasi.",
           "Nilai yang dilaporkan adalah **fungsi objektif yang benar** dievaluasi pada",
           "solusi yang dikembalikan (`true_best`), sehingga F16 pada konfigurasi",
           "`published` -- yang sebenarnya mengoptimalkan Foxholes -- terlihat apa adanya.",
           "", "## Avg (Std) per konfigurasi", ""]
    out.append("| Func | paper (KMA) | " + " | ".join(names) + " |")
    out.append("|---|---|" + "---|" * len(names))
    for fid in FUNCTIONS:
        cells = []
        for nm in names:
            s = stat(nm, fid)
            if s is None:
                cells.append("**error**")
            elif s["crashed"]:
                cells.append(f"**{s['crashed']}/{s['n']} error**")
            else:
                cells.append(f"{s['avg']:.3e} ({s['std']:.2e})")
        out.append(f"| F{fid} | {PAPER_KMA_AVG[fid]:.3e} | " + " | ".join(cells) + " |")

    out += ["", "## Guaranty: proporsi run yang mencapai ambang optimum global", "",
            "| Func | " + " | ".join(names) + " |",
            "|---|" + "---|" * len(names)]
    for fid in FUNCTIONS:
        cells = []
        for nm in names:
            s = stat(nm, fid)
            cells.append("-" if s is None or s["crashed"] else f"{s['gua']*100:.0f}%")
        out.append(f"| F{fid} | " + " | ".join(cells) + " |")

    out += ["", "## Audit anggaran evaluasi (A4)", "",
            "`counted` = NumEva seperti dihitung kode terbit; `real` = jumlah panggilan",
            "fungsi objektif yang sebenarnya. Kompetitor di Tabel 2 dibatasi 25.000.", "",
            "| Func | counted (published) | real (published) | rasio |",
            "|---|---|---|---|"]
    for fid in FUNCTIONS:
        s = stat("published", fid)
        if s is None or s["crashed"]:
            continue
        out.append(f"| F{fid} | {s['counted']:.0f} | {s['real']:.0f} | "
                   f"{s['real']/max(s['counted'],1):.3f} |")

    out += ["", "## Individu hantu akibat A2", "",
            "Jumlah maksimum baris `AllHQ` yang seluruhnya nol (posisi origin, fitness 0)",
            "yang tercipta dalam satu generasi tahap 2.", "",
            "| Func | published | fix_A2 |", "|---|---|---|"]
    for fid in FUNCTIONS:
        a, b = stat("published", fid), stat("fix_A2", fid)
        if a is None or a["crashed"] or b is None:
            continue
        out.append(f"| F{fid} | {a['zeros']} | {b['zeros']} |")

    with open(os.path.join(RESULTS, "summary.md"), "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote results/raw.csv and results/summary.md")


if __name__ == "__main__":
    main()
