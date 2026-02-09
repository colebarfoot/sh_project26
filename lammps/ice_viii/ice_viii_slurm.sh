#!/bin/bash
#
# batch script for lammps amoeba ice viii sim
#
#SBATCH --partition=long
#SBATCH --time=10:00:00
#SBATCH --mem=1G
#SBATCH --ntasks=8
#
#############################################

if [ $# -ne 1 ]; then
  echo "Required argument: [filepath]"
  exit 1
fi

srun lmp-amoeba -in $1 >"$HOME/src/sh-project/lammps/out/ice_viii.txt"
