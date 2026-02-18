#!/bin/bash
#
# batch script for lammps amoeba ice viii sim
#
#SBATCH --partition=short
#SBATCH --time=12:00:00
#SBATCH --mem=2G
#SBATCH --ntasks=64
#
#############################################

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
  -t | --temperature)
    TEMP="$2K"
    shift
    shift
    ;;
  -p | --pressure)
    PRESS="$2atm"
    shift
    shift
    ;;
  -* | --*)
    echo "unknown option $2"
    exit 1
    ;;
  *)
    POSITIONAL_ARGS+=("$1")
    shift
    ;;
  esac
done

set -- "${POSTIONAL_ARGS[@]}"

FILE="${POSITIONAL_ARGS[0]}"
IN_DIR="$(dirname $FILE)"

if [[ -z "$TEMP" ]]; then
  echo "Required argument: temp"
  exit 1
fi

if [[ -z "$PRESS" ]]; then
  echo "Required argument: press"
  exit 1
fi

if [[ -z "$FILE" ]]; then
  echo "Missing paramter: [file]"
  exit 1
else
  echo "LAMMPS script: [file]"
fi

JOB_NO="${SLURM_JOB_ID}-${TEMP}${PRESS}"

srun lmp-amoeba -in "$FILE" -var temp "$TEMP" -var press "$PRESS" >"$HOME/src/sh-project/lammps/ice_viii/.out/${JOB_NO}.txt"

mv "$IN_DIR/dump.${TEMP}K${PRESS}atm.lammpstrj" "$HOME/src/sh-project/lammps/ice_viii/.out/dump.${JOB_NO}.lammpstrj"
