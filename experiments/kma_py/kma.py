"""Faithful Python port of kma/KMA2D.m with the four defects A1-A4 switchable.

Every structural choice mirrors the MATLAB source, including the corner-based
PopConsInitialization, the 40 micro-swarms of the second stage, MutRadius=0.5,
the ">2 generations" improve/stagnation thresholds and the double MutRadius in
Reposition. Only the four findings below are toggled, so any measured difference
is attributable to the toggled defect and nothing else.

  fix_case14    (A1) Evaluation.m switch: "case 16" -> "case 14" for Foxholes
  fix_allhq     (A2) AllHQ / AllHQFX row index in the second stage
  fix_mlipir    (A3) operator precedence in the mlipir velocity, Eq.(8)
  fix_evalcount (A4) charge the 25000 budget by real objective calls

See ../../TEMUAN.md for the analysis.
"""
import math
from dataclasses import dataclass

import numpy as np

from . import benchmarks as B


@dataclass(frozen=True)
class Config:
    fix_case14: bool = False
    fix_allhq: bool = False
    fix_mlipir: bool = False
    fix_evalcount: bool = False

    @property
    def name(self):
        on = [n for n, v in (("A1", self.fix_case14), ("A2", self.fix_allhq),
                             ("A3", self.fix_mlipir), ("A4", self.fix_evalcount)) if v]
        return "published" if not on else ("all_fixed" if len(on) == 4 else "fix_" + "+".join(on))


class _Budget(Exception):
    pass


class _Run:
    def __init__(self, fid, dim, seed, cfg, max_eva=25000, pop_size=5):
        self.fid, self.cfg, self.max_eva = fid, cfg, max_eva
        self.rng = np.random.default_rng(seed)
        lo, hi, self.thr, self.nvar = B.spec(fid, dim)
        self.Rb = np.full(self.nvar, lo)
        self.Ra = np.full(self.nvar, hi)
        self.pop_size = pop_size
        self.real_evals = 0      # true number of objective calls
        self.counted = 0         # NumEva as maintained by the published code
        self.crashed = None
        self.zero_hq_rows = 0    # phantom AllHQ rows created by A2

    # ---- objective ---------------------------------------------------------
    def f(self, x):
        self.real_evals += 1
        if self.cfg.fix_evalcount and self.real_evals > self.max_eva:
            raise _Budget
        ev = B.evaluate if self.cfg.fix_case14 else B.evaluate_published
        return ev(self.fid, x, self.rng)

    def trim(self, x):
        return np.clip(x, self.Rb, self.Ra)

    # ---- initialization (corner based, as in PopConsInitialization) --------
    def cons_init(self, ps):
        F1 = np.array([0.01, 0.01, 0.99, 0.99])
        F2 = np.array([0.01, 0.99, 0.01, 0.99])
        half = self.nvar // 2
        X = np.zeros((ps, self.nvar))
        idx, nn = 0, 0
        while idx < ps:
            nl = 4 if ps - nn >= 4 else ps - nn
            for ss in range(nl):
                noise = (self.rng.random(self.nvar) * 2 - 1) * 0.01
                base = np.concatenate([np.full(half, F1[ss]),
                                       np.full(self.nvar - half, F2[ss])])
                X[idx] = self.Rb + (self.Ra - self.Rb) * (base + noise)
                idx += 1
            nn += 4
        return X

    # ---- operators ---------------------------------------------------------
    def move_big_males_female(self, BM, BMFX, Female, FemaleFX, HQ, HQFX, max_fol):
        Temp, TempFX = BM.copy(), BMFX.copy()
        for ss in range(Temp.shape[0]):
            k = self.rng.integers(1, max_fol + 1)
            VM = np.zeros(self.nvar)
            fol = 0
            for ind in self.rng.permutation(HQ.shape[0]):
                if ind != ss:
                    if HQFX[ind] < TempFX[ss] or self.rng.random() < 0.5:
                        VM += self.rng.random() * (HQ[ind] - Temp[ss])
                    else:
                        VM += self.rng.random() * (Temp[ss] - HQ[ind])
                fol += 1                       # incremented outside the if, as in the source
                if fol >= k:
                    break
            new = self.trim(Temp[ss] + VM)
            Temp[ss], TempFX[ss] = new, self.f(new)
        joint = np.vstack([BM, Temp])
        jointFX = np.concatenate([BMFX, TempFX])
        keep = np.argsort(jointFX, kind="stable")[:BM.shape[0]]
        BM, BMFX = joint[keep], jointFX[keep]

        if BMFX[0] < FemaleFX or self.rng.random() < 0.5:      # sexual reproduction
            r = self.rng.random(self.nvar)
            c1 = self.trim(r * BM[0] + (1 - r) * Female)
            c2 = self.trim(r * Female + (1 - r) * BM[0])
            f1, f2 = self.f(c1), self.f(c2)
            if f1 < f2:
                if f1 < FemaleFX:
                    Female, FemaleFX = c1, f1
            elif f2 < FemaleFX:
                Female, FemaleFX = c2, f2
        else:                                                   # parthenogenesis
            new = Female.copy()
            step = 0.5 * (self.Ra - self.Rb)                    # MutRadius = 0.5
            mask = self.rng.random(self.nvar) < 0.5             # MutRate = 0.5
            new[mask] = Female[mask] + (2 * self.rng.random(mask.sum()) - 1) * step[mask]
            new = self.trim(new)
            fx = self.f(new)
            if fx < FemaleFX:
                Female, FemaleFX = new, fx
        return BM, BMFX, Female, FemaleFX

    def move_small_males(self, SM, SMFX, HQ, mlipir_rate, max_fol):
        Temp, TempFX = SM.copy(), SMFX.copy()
        D = int(round(mlipir_rate * self.nvar))
        D = min(max(D, 1), self.nvar - 1)
        for ww in range(SM.shape[0]):
            k = 1 if max_fol == 1 else self.rng.integers(1, max_fol + 1)
            V = np.zeros(self.nvar)
            for j, ind in enumerate(self.rng.permutation(HQ.shape[0])):
                Bm = np.zeros(self.nvar)
                Bm[self.rng.permutation(self.nvar)[:D]] = 1.0
                r = self.rng.random(self.nvar)
                if self.cfg.fix_mlipir:
                    V += r * ((HQ[ind] - SM[ww]) * Bm)          # Eq.(8)
                else:
                    V += r * (HQ[ind] * Bm) - (SM[ww] * Bm)     # as published
                if j + 1 >= k:
                    break
            new = self.trim(SM[ww] + V)
            Temp[ww], TempFX[ww] = new, self.f(new)
        return Temp, TempFX

    # ---- main --------------------------------------------------------------
    def run(self):
        try:
            return self._run()
        except _Budget:
            return self._result(reached=False)
        except B.UndefinedCase as e:
            self.crashed = str(e)
            return self._result(reached=False)

    def _result(self, reached):
        best = getattr(self, "best_x", None)
        true_best = None if best is None else B.evaluate(self.fid, best, self.rng)
        return dict(fid=self.fid, config=self.cfg.name, crashed=self.crashed,
                    reported_best=getattr(self, "best_f", float("nan")),
                    true_best=true_best, reached=reached,
                    real_evals=self.real_evals, counted_evals=self.counted,
                    stage=getattr(self, "stage", 1), gens=getattr(self, "gens", 0),
                    zero_hq_rows=self.zero_hq_rows)

    def _budget_left(self):
        used = self.real_evals if self.cfg.fix_evalcount else self.counted
        return used < self.max_eva

    def _run(self):
        ps = self.pop_size
        Pop = self.cons_init(ps)
        FX = np.array([self.f(p) for p in Pop])
        o = np.argsort(FX, kind="stable")
        Pop, FX = Pop[o], FX[o]
        self.best_x, self.best_f = Pop[0].copy(), FX[0]
        one_elit = FX[0]
        num_bm = ps // 2
        min_ada, max_ada = ps * 4, ps * 40

        # ---------------- first stage ----------------
        self.stage = 1
        gen, gen_improve, improve_rate, is_global = 0, 0, 0.0, False
        while gen < 1000:
            gen += 1
            self.counted += ps
            BM, BMFX = Pop[:num_bm].copy(), FX[:num_bm].copy()
            Female, FemaleFX = Pop[num_bm].copy(), FX[num_bm]
            SM, SMFX = Pop[num_bm + 1:].copy(), FX[num_bm + 1:].copy()

            BM, BMFX, Female, FemaleFX = self.move_big_males_female(
                BM, BMFX, Female, FemaleFX, Pop[:num_bm].copy(), FX[:num_bm].copy(), 2)
            SM, SMFX = self.move_small_males(
                SM, SMFX, BM, (self.nvar - 1) / self.nvar, 1)

            Pop = np.vstack([BM, Female[None, :], SM])
            FX = np.concatenate([BMFX, [FemaleFX], SMFX])
            o = np.argsort(FX, kind="stable")
            Pop, FX = Pop[o], FX[o]
            self.best_x, self.best_f = Pop[0].copy(), FX[0]
            if FX[0] < one_elit:
                gen_improve += 1
                improve_rate = gen_improve / gen
                one_elit = FX[0]
            if FX[0] <= self.thr:
                is_global = True
                break
            if gen == 100 and improve_rate < 0.5:
                break
        self.gens = gen
        if is_global or not self._budget_left():
            return self._result(reached=is_global)

        # ---------------- second stage ----------------
        self.stage = 2
        swarm, num_bm = Pop.shape[0], Pop.shape[0] // 2
        cons = self.cons_init(max_ada - swarm)
        consFX = np.array([self.f(c) for c in cons])
        Pop = np.vstack([Pop, cons])
        FX = np.concatenate([FX, consFX])
        one_elit = FX.min()
        gen_improve = gen_stagnan = 0

        while self._budget_left():
            ada = Pop.shape[0]
            AllHQ = np.zeros((0, self.nvar))
            AllHQFX = np.zeros(0)
            for ind in range(0, ada, swarm):
                s = np.argsort(FX[ind:ind + swarm], kind="stable")[:num_bm]
                AllHQ = np.vstack([AllHQ, Pop[ind:ind + swarm][s]])
                AllHQFX = np.concatenate([AllHQFX, FX[ind:ind + swarm][s]])

            for ind in range(0, ada, swarm):
                s = np.argsort(FX[ind:ind + swarm], kind="stable")
                ms, msfx = Pop[ind:ind + swarm][s], FX[ind:ind + swarm][s]
                BM, BMFX = ms[:num_bm].copy(), msfx[:num_bm].copy()
                Female, FemaleFX = ms[num_bm].copy(), msfx[num_bm]
                SM, SMFX = ms[num_bm + 1:].copy(), msfx[num_bm + 1:].copy()

                GHQ = np.vstack([BM, AllHQ]) if AllHQ.size else BM
                GHQFX = np.concatenate([BMFX, AllHQFX]) if AllHQ.size else BMFX
                BM, BMFX, Female, FemaleFX = self.move_big_males_female(
                    BM, BMFX, Female, FemaleFX, GHQ, GHQFX, 3)
                HQ = np.vstack([BM, AllHQ]) if AllHQ.size else BM
                SM, SMFX = self.move_small_males(SM, SMFX, HQ, 0.5, 3)

                # ---- finding A2 lives here ----
                at = (ind // swarm) * num_bm if self.cfg.fix_allhq else ind
                need = at + num_bm
                if need > AllHQ.shape[0]:      # MATLAB grows with zeros
                    pad = need - AllHQ.shape[0]
                    AllHQ = np.vstack([AllHQ, np.zeros((pad, self.nvar))])
                    AllHQFX = np.concatenate([AllHQFX, np.zeros(pad)])
                AllHQ[at:need], AllHQFX[at:need] = BM, BMFX

                Pop[ind:ind + swarm] = np.vstack([BM, Female[None, :], SM])
                FX[ind:ind + swarm] = np.concatenate([BMFX, [FemaleFX], SMFX])
                self.counted += swarm
                if FX.min() <= self.thr:
                    break

            self.zero_hq_rows = max(self.zero_hq_rows,
                                    int(np.sum(np.all(AllHQ == 0, axis=1))))
            p = self.rng.permutation(len(FX))
            Pop, FX = Pop[p], FX[p]
            i = int(np.argmin(FX))
            self.best_x, self.best_f = Pop[i].copy(), FX[i]
            self.gens += 1
            if FX[i] <= self.thr:
                return self._result(reached=True)

            if FX[i] < one_elit:
                gen_improve, gen_stagnan, one_elit = gen_improve + 1, 0, FX[i]
            else:
                gen_stagnan, gen_improve = gen_stagnan + 1, 0

            if gen_improve > 2:                       # MaxGenImprove = 2
                ada = max(ada - swarm, min_ada)
                o = np.argsort(FX, kind="stable")
                Pop, FX = Pop[o][:ada].copy(), FX[o][:ada].copy()
                gen_improve = 0

            if gen_stagnan > 2:                       # MaxGenStagnan = 2
                old = Pop.shape[0]
                if old + swarm > max_ada:             # Reposition branch
                    step = 0.5 * 0.5 * (self.Ra - self.Rb)   # double MutRadius, as in source
                    for nn in range(old):
                        cand = Pop[nn].copy()
                        mask = self.rng.random(self.nvar) < 0.5
                        cand[mask] = Pop[nn][mask] + (2 * self.rng.random(mask.sum()) - 1) * step[mask]
                        cand = self.trim(cand)
                        cf = self.f(cand)
                        if cf < FX[nn]:
                            Pop[nn], FX[nn] = cand, cf
                    self.counted += old
                else:                                 # AddingPop branch (Levy)
                    best = Pop[int(np.argmin(FX))]
                    new = np.array([self.trim(best + 0.05 * _levy(self.rng, self.nvar, 1.5)
                                              * np.abs(self.Ra - self.Rb))
                                    for _ in range(swarm)])
                    newFX = np.array([self.f(x) for x in new])
                    Pop, FX = np.vstack([Pop, new]), np.concatenate([FX, newFX])
                    self.counted += swarm
                gen_stagnan = 0

        return self._result(reached=False)


def _levy(rng, m, beta):
    num = math.gamma(1 + beta) * np.sin(np.pi * beta / 2)
    den = math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2)
    sigma = (num / den) ** (1 / beta)
    u = rng.normal(0, sigma, m)
    v = rng.normal(0, 1, m)
    return u / np.abs(v) ** (1 / beta)


def run(fid, dim, seed, cfg, max_eva=25000):
    return _Run(fid, dim, seed, cfg, max_eva).run()
