#!/bin/bash
# 
# date: 30-01-2026
# author: Cole Barfoot
# batch script for high pressure ice LAMMPS 
# AMOEBA simulation
#
#SBATCH --partition=long
#SBATCH --time=4-00:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=16
#
#############################################

POSITIONAL_ARGS=()

JOB_NO=${SLURM_JOB_ID}

# get cmdline options
while [[ $# -gt 0 ]]; do
  case $1 in
  -t | --temperature)
    TEMP="$2K"
    JOB_NO="${JOB_NO}-${TEMP}K"
    shift
    shift
    ;;
  -p | --pressure)
    PRESS="$2atm"
    JOB_NO="${JOB_NO}-${PRESS}K"
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

if [[ -z "$FILE" ]]; then
  echo "Missing paramter: [file]"
  exit 1
else
  echo "LAMMPS script: $FILE"
fi

# if temperature and pressure not specified,
# simulation will run with default conditions
RUN="srun lmp-amoeba -in ${FILE}"
OUT="$HOME/src/sh-project/lammps/out/${JOB_NO}.txt"
if ! [[ -z "$TEMP" ]]; then RUN="${RUN} -var temp ${TEMP}"; fi
if ! [[ -z "$PRESS" ]]; then
  RUN="${RUN} -var press ${PRESS}"
  eval "${RUN}>${OUT}"
else
  eval "${RUN}>${OUT}"
fi
