#!/bin/bash
#
# array batch script for lammps amoeba ice viii sim
#
#SBATCH --partition=long
#SBATCH --time=1-00:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=32
#SBATCH --array=1-9
#
#############################################

POSITIONAL_ARGS=()

while [[ $# -ne 0 ]]; do
  case $1 in
  -p | --p)
    PARAM_FILE=$2
    shift
    shift
    ;;
  -* | --*)
    echo "Unknown option: $2"
    exit 1
    ;;
  *)
    POSITIONAL_ARGS+=("$1")
    shift
    ;;
  esac
done

set -- "${POSTIONAL_ARGS[@]}"

IN_FILE="${POSITIONAL_ARGS[0]}"
IN_DIR="$(dirname $IN_FILE)"

if [[ -z "$PARAM_FILE" ]]; then
  echo "Required parameter: [param_file]"
  exit 1
else
  echo "Parameter file: ${PARAM_FILE}"
fi

if [[ -z "$IN_FILE" ]]; then
  echo "Missing paramter: [file]"
  exit 1
else
  echo "LAMMPS script: ${IN_FILE}"
fi

found=0
while IFS= read -r line; do
  IFS=' ' read -r -a paramarr <<<"$line"

  if [[ "${paramarr[0]}" == "$SLURM_ARRAY_TASK_ID" ]]; then
    found=1
    T="${paramarr[1]}"
    P="${paramarr[2]}"
    echo "Temperature: ${T}K"
    echo "Pressure: ${P}atm"

    echo "Array ID: ${SLURM_ARRAY_TASK_ID}"

    srun lmp-amoeba \
      -in "$IN_FILE" \
      -var temp "$T" \
      -var press "$P" \
      >"$HOME/src/sh-project/lammps/ice_viii/.out/${SLURM_JOB_ID}-${T}K${P}atm.txt"

    mv "$IN_DIR/dump.${T}K${P}atm.lammpstrj" "$HOME/src/sh-project/lammps/ice_viii/.out/dump.${SLURM_JOB_ID}-${T}K${P}atm.lammpstrj"

    break
  fi
done <"$PARAM_FILE"

if ((!found)); then
  echo "Array indices do not match"
  exit 1
fi
