#!/usr/bin/bash
#
# file: last_averages.sh
# date: 19-03-2025
# author: Cole Barfoot
# script to compute time averages of lammps thermo data
# via python data analysis script
#
#########################################################

keys=("Temp" "Volume" "Press" "TotEng" "HMSD" "OMSD" "Enthalpy" "HBONDS" "HVACF" "OVACF" "BoxRatio")

positional_args=()
gibbs=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t | --type)
            ice_type="$2"
            shift
            shift
            ;;
        -g | --gibbs)
            keys+=("Gibbs")
            gibbs=1
            shift
            ;;
        -*)
            echo "unknown option $1"
            exit 1
            ;;
        *)
            positional_args+=("$1")
            shift
            ;;
    esac
done

if [[ -z "$ice_type" ]]; then
    echo "no type specified"
    exit 1
fi

if [[ ${#positional_args[@]} -gt 1 ]]; then
    echo "too many arguments"
    exit 1
fi

indir="${positional_args[@]}"
if [[ ! -d "$indir" ]]; then
    echo "not a valid directory"
    exit 1
fi

out="${indir}/../plots/last${ice_type}.txt"

header=()
for key in "${keys[@]}"; do
    header+=("$key" "${key}_std")
done
echo "${header[@]}" > "$out"

for file in "$indir"/parsed-isotherm"$ice_type"-*; do
    if ((gibbs)); then
        ./data_analysis.py -g -i "$ice_type" --last -k "${keys[@]}" "$file"
    else
        ./data_analysis.py -i "$ice_type" --last -k "${keys[@]}" "$file"
    fi
done >> "$out"
