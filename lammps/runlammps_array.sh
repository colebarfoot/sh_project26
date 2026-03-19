#!/bin/bash
#
# array batch script for lammps amoeba high pressure ice simulation
#
#SBATCH --partition=long
#SBATCH --time=6-00:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=8
#SBATCH --array=1-30
#
#############################################

POSITIONAL_ARGS=()

while [[ $# -ne 0 ]]; do
  case $1 in
  -p | --param)
    PARAM_FILE=$2
    shift
    shift
    ;;
  -* | --*)
    echo "Unknown option: $1"
    exit 1
    ;;
  *)
    POSITIONAL_ARGS+=("$1")
    shift
    ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}"

IN_FILE="$1"
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
    echo "Temperature: ${T}"
    echo "Pressure: ${P}"

    echo "Array ID: ${SLURM_ARRAY_TASK_ID}"

    mkdir -p "$HOME/src/sh-project/lammps/out"

    srun lmp-amoeba \
      -in "$IN_FILE" \
      -var temp "$T" \
      -var press "$P" \
      -var jobid "$SLURM_JOB_ID" \
      >"$HOME/src/sh-project/lammps/out/isotherm-${SLURM_JOB_ID}-${T}K-${P}atm.txt"

    break
  fi
done <"$PARAM_FILE"

if ((!found)); then
  echo "Array indices do not match"
  exit 1
fi
