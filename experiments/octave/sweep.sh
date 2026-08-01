#!/bin/bash
# Verification sweep with real GNU Octave: baseline kma/ vs kma-fixed/.
export MAMBA_ROOT_PREFIX="$HOME/.local/micromamba"
OCT="$HOME/.local/micromamba/bin/micromamba run -n oct octave-cli"
cd "$(dirname "$0")/../.."
for f in 1 5 6 9 10 11; do
  for s in 1 2 3; do
    for dir in kma kma-fixed; do
      printf '%-10s ' "$dir"
      timeout 1800 $OCT experiments/octave/run_one.m "$dir" "$f" 50 "$s" 2>/dev/null | grep -E '^status' || echo "status=timeout fid=$f seed=$s"
    done
  done
done
for f in 14 16; do
  for s in 1 2 3; do
    for dir in kma kma-fixed; do
      printf '%-10s ' "$dir"
      timeout 1800 $OCT experiments/octave/run_one.m "$dir" "$f" 2 "$s" 2>/dev/null | grep -E '^status' || echo "status=timeout fid=$f seed=$s"
    done
  done
done
