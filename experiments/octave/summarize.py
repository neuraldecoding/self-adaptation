#!/usr/bin/env python3
"""Ringkas hasil sweep Octave menjadi tabel bergaya Tabel 2 manuskrip.

    python3 summarize.py ../results/octave_verification.txt

Menghitung Avg dan Std per fungsi per versi, ditambah Guaranty: proporsi run yang
mencapai ambang optimum global yang dipakai kode itu sendiri (FthresholdFX dari
GetFunction.m). Ambang itu bukan optimum sejati untuk beberapa fungsi -- F21
misalnya punya minimum -10.15319968 sementara ambangnya -10.1532, sehingga
tidak pernah tercapai.
"""
import re
import statistics as st
import sys
from collections import defaultdict

# Avg KMA pada Tabel 2 manuskrip (dimensi 50 untuk F1-F13).
PAPER = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 4.831e1, 6: 0.0, 7: 1.715e-4,
         8: -1.701e4, 9: 0.0, 10: 8.882e-16, 11: 0.0, 12: 2.799e-3, 13: 5.270e-2,
         14: 9.980e-1, 15: 3.075e-4, 16: -1.032, 17: 3.979e-1, 18: 3.0,
         19: -3.861, 20: -3.320, 21: -10.1532, 22: -10.4029, 23: -10.5364}
# FthresholdFX dari GetFunction.m; F8 bergantung dimensi.
THR = dict(PAPER)
THR.update({5: 0.0, 7: 0.0, 8: -418.9829 * 50, 10: 0.0, 12: 0.0, 13: 0.0,
            15: 0.0003, 16: -1.0316, 17: 0.398, 19: -3.86, 20: -3.32})
NAME = {1: 'Sphere', 2: 'Schwefel 2.22', 3: 'Schwefel 1.2', 4: 'Schwefel 2.21',
        5: 'Rosenbrock', 6: 'Step', 7: 'Quartic', 8: 'Schwefel', 9: 'Rastrigin',
        10: 'Ackley', 11: 'Griewank', 12: 'Penalized', 13: 'Penalized2',
        14: 'Foxholes', 15: 'Kowalik', 16: 'Six Hump Camel', 17: 'Branin',
        18: 'Goldstein-Price', 19: 'Hartman 3', 20: 'Hartman 6',
        21: 'Shekel 5', 22: 'Shekel 7', 23: 'Shekel 10'}


def parse(path):
    data = defaultdict(list)
    for line in open(path):
        if line.startswith('#') or not line.strip():
            continue
        d = line.split()[0]
        fid = int(re.search(r'fid=(\d+)', line).group(1))
        if 'status=ok' not in line:
            data[(fid, d)].append(None)
            continue
        data[(fid, d)].append((float(re.search(r'opt=(\S+)', line).group(1)),
                               int(re.search(r'numeva=(\d+)', line).group(1))))
    return data


def cell(vals):
    if any(v is None for v in vals):
        n = sum(1 for v in vals if v is None)
        return f'**error {n}/{len(vals)}**', '', ''
    opt = [v[0] for v in vals]
    ev = [v[1] for v in vals]
    return f'{st.mean(opt):.4e}', f'{st.pstdev(opt):.2e}', f'{st.mean(ev):.1f}'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else '../results/octave_verification.txt'
    data = parse(path)
    fids = sorted({f for f, _ in data})
    n = len(data[(fids[0], 'kma')])

    print(f'# Ringkasan sweep Octave ({n} seed per sel)\n')
    print('Avg (Std) dan MFE dari menjalankan sumber MATLAB apa adanya di GNU Octave.')
    print('Kolom manuskrip adalah Avg KMA pada Tabel 2.\n')
    print('| Func | Nama | `kma/` Avg (Std) | manuskrip | `kma-fixed/` Avg (Std) | `kma/` MFE |')
    print('|---|---|---|---|---|---|')
    for f in fids:
        a, sa, ea = cell(data[(f, 'kma')])
        b, sb, _ = cell(data[(f, 'kma-fixed')])
        ca = a if not sa else f'{a} ({sa})'
        cb = b if not sb else f'{b} ({sb})'
        print(f'| F{f} | {NAME[f]} | {ca} | {PAPER[f]:.4g} | {cb} | {ea or "-"} |')

    print('\n## Guaranty: proporsi run yang mencapai ambang kode sendiri\n')
    print('| Func | `kma/` | `kma-fixed/` |')
    print('|---|---|---|')
    for f in fids:
        row = []
        for d in ('kma', 'kma-fixed'):
            vals = data[(f, d)]
            if any(v is None for v in vals):
                row.append('error')
            else:
                hit = sum(1 for v in vals if v[0] <= THR[f])
                row.append(f'{hit/len(vals)*100:.0f}%')
        print(f'| F{f} | {row[0]} | {row[1]} |')


if __name__ == '__main__':
    main()
