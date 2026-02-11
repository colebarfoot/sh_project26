#!/bin/bash
#
# shell script to convert exyz files produced by genice2.py
# to amoeba lammps files using the tinker2lmp.py and exyz2tinker.py
# tools and the amoeba_water.prm file from the amoeba water example
#
#
###################################################################

if [ $# -ne 1 ]; then
  echo "Required argument: [filepath]"
  exit 1
fi

# extract filepath and dir
DIR="$(dirname "$1")"
FILE="$(basename "$1")"
FILE="${FILE%.xyz}"

# run the intermediate conversion
"$HOME"/src/sh-project/utils/xyz2tinker.py $1

# run final conversion
python "$HOME"/src/sh-project/utils/tinker2lmp.py -xyz "${DIR}/${FILE}.tinker" \
  -amoeba "${DIR}/amoeba_water.prm" \
  -data "${DIR}/data.${FILE%.xyz}.amoeba"
