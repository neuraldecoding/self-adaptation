#!/bin/bash
# Verification sweep with real GNU Octave: baseline kma/ vs kma-fixed/.
#
#   ./sweep.sh                 # all 23 functions
#   ./sweep.sh 2 3 4           # only the listed functions
#
# F1-F13 are run at dimension 50. For F14-F23 the dimension argument is ignored:
# GetFunction overrides Nvar with the fixed dimension of the function.
export MAMBA_ROOT_PREFIX="$HOME/.local/micromamba"
OCT="$HOME/.local/micromamba/bin/micromamba run -n oct octave-cli"
cd "$(dirname "$0")/../.."

SEEDS="1 2 3"
if [ $# -gt 0 ]; then
  FUNCS="$*"
else
  FUNCS=$(seq 1 23)
fi

for f in $FUNCS; do
  if [ "$f" -le 13 ]; then dim=50; else dim=2; fi
  for s in $SEEDS; do
    for dir in kma kma-fixed; do
      printf '%-10s ' "$dir"
      timeout 1800 $OCT experiments/octave/run_one.m "$dir" "$f" "$dim" "$s" 2>/dev/null \
        | grep -E '^status' || echo "status=timeout fid=$f seed=$s"
    done
  done
done
