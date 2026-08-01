#!/bin/bash
# Verification sweep with real GNU Octave: baseline kma/ vs kma-fixed/.
#
#   ./sweep.sh                 # F1-F13 at dim 50, plus F14 and F16
#   ./sweep.sh 2 3 4           # only the listed high-dimensional functions
#
# Fixed-dimension functions F14 and F16 are appended only when no argument is
# given, since their dimension comes from GetFunction, not from the caller.
export MAMBA_ROOT_PREFIX="$HOME/.local/micromamba"
OCT="$HOME/.local/micromamba/bin/micromamba run -n oct octave-cli"
cd "$(dirname "$0")/../.."

SEEDS="1 2 3"
if [ $# -gt 0 ]; then
  HD="$*"
  FD=""
else
  HD="1 2 3 4 5 6 7 8 9 10 11 12 13"
  FD="14 16"
fi

for f in $HD; do
  for s in $SEEDS; do
    for dir in kma kma-fixed; do
      printf '%-10s ' "$dir"
      timeout 1800 $OCT experiments/octave/run_one.m "$dir" "$f" 50 "$s" 2>/dev/null \
        | grep -E '^status' || echo "status=timeout fid=$f seed=$s"
    done
  done
done

for f in $FD; do
  for s in $SEEDS; do
    for dir in kma kma-fixed; do
      printf '%-10s ' "$dir"
      timeout 1800 $OCT experiments/octave/run_one.m "$dir" "$f" 2 "$s" 2>/dev/null \
        | grep -E '^status' || echo "status=timeout fid=$f seed=$s"
    done
  done
done
