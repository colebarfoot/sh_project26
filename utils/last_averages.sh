#!/usr/bin/bash

keys=("Temp" "Volume" "Press" "TotEng" "HMSD" "OMSD" "Enthalpy" "HBONDS")

positional_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t | --type)
            type="$2"
            shift
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

dir="${positional_args[@]}"
if [[ ! -d "$dir" ]]; then
    echo "not a valid directory"
    exit 1
fi

out="${dir}/last${type}.txt"
echo "${keys[@]}" > "$out"

for file in "$dir"/parsed-isotherm"$type"-*; do
    ./data_analysis.py -i 7 --last -k "${keys[@]}" "$file"
done >> "$out"
