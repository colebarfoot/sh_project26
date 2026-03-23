#!/usr/bin/bash
#
#
#
#
#

if [[ $# -gt 1 ]]; then
    echo "too many arguments"
    exit 1
fi

type=7
thermo_file="$1"
out="$(dirname "$1")/../plots/equilib.txt"

./data_analysis.py -d -i "$type" -s 1000,500000 -k Timestep Temp "$thermo_file" > "$out"
