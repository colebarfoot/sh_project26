#!/usr/bin/bash

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

indir="${positional_args[@]}"
if [[ ! -d "$indir" ]]; then
    echo "not a valid directory"
    exit 1
fi
out="${indir}/../plots"

for file in "$indir"/parsed-isotherm"$type"-*; do
    new="$(basename "$file")"
    new="${new#parsed-isotherm"$type"-}"
    new="${new#*-}"
    new="${new%-*}"
    ./data_analysis.py -i "$type" -r last,OO_rdf "$file" > "${out}/oo_rdf${type}-${new}-last.txt"
    ./data_analysis.py -i "$type" -r last,OH_rdf "$file" > "${out}/oh_rdf${type}-${new}-last.txt"
    ./data_analysis.py -i "$type" -r last,HH_rdf "$file" > "${out}/hh_rdf${type}-${new}-last.txt"
    echo "${file} done"
done
