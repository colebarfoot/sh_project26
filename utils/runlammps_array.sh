#!/bin/bash
#
# array batch script for LAMMPS AMOEBA high pressure
# ice simulation
#
#SBATCH --partition=long
#SBATCH --time=4-00:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=16
#SBATCH --array=1-16
#
#############################################

POSITIONAL_ARGS=()

# get cmdline options
while [[ $# -ne 0 ]]; do
  case "$1" in
  -p | --param)
    PARAM_FILE="$2"
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
IN_DIR="$(dirname "$IN_FILE")"

if [[ -z "$PARAM_FILE" ]]; then
  echo "parameter file required"
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

# assigning each slurm array to a simulation
# with distinct conditions
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
    
    # note!! this will not throw an error if
    # 'temp', 'press' etc. does not match the 
    # variable name in the LAMMPS script but
    # all simulations will run with default 
    # conditions
    srun lmp-amoeba \
      -in "$IN_FILE" \
      -var temp "$T" \
      -var press "$P" \
      -var jobid="$SLURM_JOB_ID" \
      >"$HOME/src/sh-project/lammps/out/isotherm-${SLURM_JOB_ID}-${T}K-${P}atm.txt"

    break
  fi
done <"$PARAM_FILE"

if ((!found)); then
  echo "Array indices do not match"
  exit 1
fi
