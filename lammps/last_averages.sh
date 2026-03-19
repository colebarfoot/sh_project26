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
            type="$2"
            shift
            shift
            ;;
        -g | --gibbs)
            keys+=("Gibbs")
            gibbs="-g"
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

if [[ -z "$type" ]]; then
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

out="${indir}/../plots/last${type}.txt"
header=()
for key in "${keys[@]}"; do
    header+=("$key" "${key}_std")
done
echo "${header[@]}" > "$out"

for file in "$indir"/parsed-isotherm"$type"-*; do
    ./data_analysis.py "$gibbs" -i "$type" --last -k "${keys[@]}" "$file"
done >> "$out"
