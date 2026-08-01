"""The 23 classic benchmark functions used by KMA.

Translated 1:1 from kma/Evaluation.m and kma/GetFunction.m. Two dispatchers are
provided so the effect of finding A1 (see ../../TEMUAN.md) can be measured:

  evaluate()          -- correct dispatch, F14 = Foxholes, F16 = Six Hump Camel
  evaluate_published()-- reproduces the published switch, where the Foxholes
                         block is labelled "case 16": F14 matches no case and
                         F16 silently runs Foxholes.
"""
import numpy as np

# (lower, upper, threshold-used-as-global-optimum, nvar or None = user dimension)
_SPEC = {
    1:  (-100.0, 100.0, 0.0, None),
    2:  (-10.0, 10.0, 0.0, None),
    3:  (-100.0, 100.0, 0.0, None),
    4:  (-100.0, 100.0, 0.0, None),
    5:  (-30.0, 30.0, 0.0, None),
    6:  (-100.0, 100.0, 0.0, None),
    7:  (-1.28, 1.28, 0.0, None),
    8:  (-500.0, 500.0, None, None),   # threshold = -418.9829 * nvar
    9:  (-5.12, 5.12, 0.0, None),
    10: (-32.0, 32.0, 0.0, None),
    11: (-600.0, 600.0, 0.0, None),
    12: (-50.0, 50.0, 0.0, None),
    13: (-50.0, 50.0, 0.0, None),
    14: (-65.0, 65.0, 0.998, 2),
    15: (-5.0, 5.0, 0.0003, 4),
    16: (-5.0, 5.0, -1.0316, 2),
    17: (-5.0, 5.0, 0.398, 2),
    18: (-2.0, 2.0, 3.0, 2),
    19: (0.0, 1.0, -3.86, 3),
    20: (0.0, 1.0, -3.32, 6),
    21: (0.0, 10.0, -10.1532, 4),
    22: (0.0, 10.0, -10.4029, 4),
    23: (0.0, 10.0, -10.5364, 4),
}

_SHEKEL_A = np.array([[4., 4, 4, 4], [1, 1, 1, 1], [8, 8, 8, 8], [6, 6, 6, 6],
                      [3, 7, 3, 7], [2, 9, 2, 9], [5, 5, 3, 3], [8, 1, 8, 1],
                      [6, 2, 6, 2], [7, 3.6, 7, 3.6]])
_SHEKEL_C = np.array([0.1, 0.2, 0.2, 0.4, 0.4, 0.6, 0.3, 0.7, 0.5, 0.5])
_FOX_A = np.array([
    [-32., -16, 0, 16, 32] * 5,
    [-32.] * 5 + [-16.] * 5 + [0.] * 5 + [16.] * 5 + [32.] * 5])
_H3_A = np.array([[3., 10, 30], [.1, 10, 35], [3, 10, 30], [.1, 10, 35]])
_H3_C = np.array([1., 1.2, 3, 3.2])
_H3_P = np.array([[.3689, .117, .2673], [.4699, .4387, .747],
                  [.1091, .8732, .5547], [.03815, .5743, .8828]])
_H6_A = np.array([[10., 3, 17, 3.5, 1.7, 8], [.05, 10, 17, .1, 8, 14],
                  [3, 3.5, 1.7, 10, 17, 8], [17, 8, .05, 10, .1, 14]])
_H6_C = np.array([1., 1.2, 3, 3.2])
_H6_P = np.array([[.1312, .1696, .5569, .0124, .8283, .5886],
                  [.2329, .4135, .8307, .3736, .1004, .9991],
                  [.2348, .1415, .3522, .2883, .3047, .6650],
                  [.4047, .8828, .8732, .5743, .1091, .0381]])
_KOW_A = np.array([.1957, .1947, .1735, .16, .0844, .0627, .0456, .0342,
                   .0323, .0235, .0246])
_KOW_B = 1.0 / np.array([.25, .5, 1, 2, 4, 6, 8, 10, 12, 14, 16])


class UndefinedCase(Exception):
    """Raised when the published switch has no case for the requested F-id."""


def spec(fid, dim):
    lo, hi, thr, fixed = _SPEC[fid]
    nvar = fixed if fixed is not None else dim
    if thr is None:                       # F8
        thr = -418.9829 * nvar
    return lo, hi, thr, nvar


def _foxholes(x):
    b = np.sum((x[:, None] - _FOX_A[:len(x)]) ** 6, axis=0)
    return float((1.0 / 500 + np.sum(1.0 / (np.arange(1, 26) + b))) ** -1)


def evaluate(fid, x, rng=None):
    x = np.asarray(x, dtype=float)
    n = x.size
    if fid == 1:
        return float(np.sum(x ** 2))
    if fid == 2:
        return float(np.sum(np.abs(x)) + np.prod(np.abs(x)))
    if fid == 3:
        return float(np.sum(np.cumsum(x) ** 2))
    if fid == 4:
        return float(np.max(np.abs(x)))
    if fid == 5:
        return float(np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (x[:-1] - 1) ** 2))
    if fid == 6:
        return float(np.sum(np.floor(x + 0.5) ** 2))
    if fid == 7:
        return float(np.sum(np.arange(1, n + 1) * x ** 4) + (rng or np.random).random())
    if fid == 8:
        return float(np.sum(-x * np.sin(np.sqrt(np.abs(x)))))
    if fid == 9:
        return float(np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)) + 10 * n)
    if fid == 10:
        return float(-20 * np.exp(-.2 * np.sqrt(np.sum(x ** 2) / n))
                     - np.exp(np.sum(np.cos(2 * np.pi * x)) / n) + 20 + np.e)
    if fid == 11:
        return float(np.sum(x ** 2) / 4000
                     - np.prod(np.cos(x / np.sqrt(np.arange(1, n + 1)))) + 1)
    if fid == 12:
        a, k, m = 10, 100, 4
        y = 1 + (x + 1) / 4
        return float((np.pi / n) * (10 * np.sin(np.pi * y[0]) ** 2
                     + np.sum((y[:-1] - 1) ** 2 * (1 + 10 * np.sin(np.pi * y[1:]) ** 2))
                     + (y[-1] - 1) ** 2)
                     + np.sum(k * (x - a) ** m * (x > a) + k * (-x - a) ** m * (x < -a)))
    if fid == 13:
        a, k, m = 5, 100, 4
        return float(.1 * (np.sin(3 * np.pi * x[0]) ** 2
                     + np.sum((x[:-1] - 1) ** 2 * (1 + np.sin(3 * np.pi * x[1:]) ** 2))
                     + (x[-1] - 1) ** 2 * (1 + np.sin(2 * np.pi * x[-1]) ** 2))
                     + np.sum(k * (x - a) ** m * (x > a) + k * (-x - a) ** m * (x < -a)))
    if fid == 14:
        return _foxholes(x)
    if fid == 15:
        return float(np.sum((_KOW_A - (x[0] * (_KOW_B ** 2 + x[1] * _KOW_B))
                             / (_KOW_B ** 2 + x[2] * _KOW_B + x[3])) ** 2))
    if fid == 16:
        return float(4 * x[0] ** 2 - 2.1 * x[0] ** 4 + x[0] ** 6 / 3
                     + x[0] * x[1] - 4 * x[1] ** 2 + 4 * x[1] ** 4)
    if fid == 17:
        return float((x[1] - x[0] ** 2 * 5.1 / (4 * np.pi ** 2) + 5 / np.pi * x[0] - 6) ** 2
                     + 10 * (1 - 1 / (8 * np.pi)) * np.cos(x[0]) + 10)
    if fid == 18:
        return float((1 + (x[0] + x[1] + 1) ** 2 * (19 - 14 * x[0] + 3 * x[0] ** 2
                      - 14 * x[1] + 6 * x[0] * x[1] + 3 * x[1] ** 2))
                     * (30 + (2 * x[0] - 3 * x[1]) ** 2 * (18 - 32 * x[0] + 12 * x[0] ** 2
                        + 48 * x[1] - 36 * x[0] * x[1] + 27 * x[1] ** 2)))
    if fid == 19:
        return float(-np.sum(_H3_C * np.exp(-np.sum(_H3_A * (x - _H3_P) ** 2, axis=1))))
    if fid == 20:
        return float(-np.sum(_H6_C * np.exp(-np.sum(_H6_A * (x - _H6_P) ** 2, axis=1))))
    if fid in (21, 22, 23):
        m = {21: 5, 22: 7, 23: 10}[fid]
        d = x - _SHEKEL_A[:m]
        return float(-np.sum(1.0 / (np.sum(d * d, axis=1) + _SHEKEL_C[:m])))
    raise UndefinedCase(f"no case for F{fid}")


def evaluate_published(fid, x, rng=None):
    """Dispatch exactly as kma/Evaluation.m does (finding A1)."""
    if fid == 14:
        raise UndefinedCase("F14 matches no case in the published switch")
    if fid == 16:
        return _foxholes(np.asarray(x, dtype=float))   # first matching case wins
    return evaluate(fid, x, rng)
