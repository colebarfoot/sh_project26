#!/bin/bash
#
# batch script for lammps amoeba ice viii sim
#
#SBATCH --partition=long
#SBATCH --time=12:00:00
#SBATCH --mem=2G
#SBATCH --ntasks=64
#
#############################################

POSITIONAL_ARGS=()
TEMP=""
PRESS=""
VOL=""

while [[ $# -gt 0 ]]; do
  case $1 in
  -f | --file)
    FILE=$2
    shift
    shift
    ;;
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
  -v | --volume)
    VOL="$2a3"
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

JOB_NO="${SLURM_JOB_ID}-${TEMP}${PRESS}${VOL}"
IN_DIR="$(dirname $FILE)"

srun lmp-amoeba -in ${FILE} >"$HOME/src/sh-project/lammps/ice_viii/.out/${JOB_NO}.txt"

mv "$IN_DIR/dump.lammpstrj" "$HOME/src/sh-project/lammps/ice_viii/.out/dump.${JOB_NO}.lammpstrj"
