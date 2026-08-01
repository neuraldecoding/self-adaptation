#!/bin/bash
# Verification sweep with real GNU Octave: baseline kma/ vs kma-fixed/.
#
#   ./sweep.sh                          # all 23 functions, 3 seeds, serial
#   ./sweep.sh 2 3 4                    # only the listed functions
#   SEEDS=30 JOBS=10 ./sweep.sh         # 30 seeds on 10 workers (~30 min)
#
# F1-F13 are run at dimension 50. For F14-F23 the dimension argument is ignored:
# GetFunction overrides Nvar with the fixed dimension of the function.
#
# Each run writes its own file under a scratch directory before the results are
# concatenated, so parallel workers cannot interleave partial lines.
set -u
export MAMBA_ROOT_PREFIX="$HOME/.local/micromamba"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SEEDS=${SEEDS:-3}
JOBS=${JOBS:-1}
if [ $# -gt 0 ]; then FUNCS="$*"; else FUNCS=$(seq 1 23); fi

SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT

run_one() {
    local dir=$1 fid=$2 seed=$3 dim
    if [ "$fid" -le 13 ]; then dim=50; else dim=2; fi
    local out
    out=$(timeout 1800 "$HOME/.local/micromamba/bin/micromamba" run -n oct \
              octave-cli experiments/octave/run_one.m "$dir" "$fid" "$dim" "$seed" 2>/dev/null \
          | grep -E '^status')
    [ -n "$out" ] || out="status=timeout fid=$fid seed=$seed"
    printf '%-10s %s\n' "$dir" "$out" > "$SCRATCH/$(printf '%02d_%02d_%s' "$fid" "$seed" "$dir")"
}
export -f run_one
export SCRATCH ROOT

for f in $FUNCS; do
    for s in $(seq 1 "$SEEDS"); do
        for dir in kma kma-fixed; do
            printf '%s %s %s\n' "$dir" "$f" "$s"
        done
    done
done | xargs -P "$JOBS" -n 3 bash -c 'run_one "$0" "$1" "$2"'

cat "$SCRATCH"/*
