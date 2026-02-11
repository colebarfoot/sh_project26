#!/bin/bash
#
# batch script for lammps amoeba ice viii sim
#
#SBATCH --partition=short
#SBATCH --time=12:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=16
#
#############################################

if [ $# -ne 1 ]; then
  echo "Required argument: [filepath]"
  exit 1
fi

srun lmp-amoeba -in $1 >"$HOME/src/sh-project/lammps/ice_viii/.out/${SLURM_JOB_ID}.out"

mv dump.lammpstrj "$HOME/src/sh-project/lammps/ice_viii/.out/dump.${SLURM_JOB_ID}.lammpstrj"
