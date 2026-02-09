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
FILENAME="${FILE%.exyz}"

# file locations
PRM_DIR="${DIR}/../prm"
TINKER_DIR="${DIR}/../tinker"
OUTPUT_DIR="${DIR}/../amoeba"

# run the intermediate conversion
./exyz2tinker.py $1

# run final conversion
python ./tinker2lmp.py -xyz "${TINKER_DIR}/${FILENAME}.xyz" \
  -amoeba "${PRM_DIR}/amoeba_water.prm" \
  -data "${OUTPUT_DIR}/data.${FILENAME}.amoeba"
