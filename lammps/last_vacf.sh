#!/usr/bin/bash
#
#
#
#
#
#

positional_args=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t | --type)
            type="$2"
            shift 2
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
    echo "type not specified"
    exit 1
fi

if [[ ${#positional_args[@]} -gt 1 ]]; then
    echo "too many args"
    exit 1
fi

indir="${positional_args[@]}"

if [[ ! -d "$indir" ]]; then
    echo "specify a directory"
    exit 1
fi

out="${indir}/../plots/"
for thermo_file in "$indir"/parsed-isotherm"$type"-*; do
    temp="$(basename "$thermo_file")"
    temp="${temp#parsed-isotherm"$type"-}"
    temp="${temp#*-}"
    temp="${temp%-*}"
    ./data_analysis.py -i "$type" --startstop 2990000,3000000 --phonon "$thermo_file" \
        > "${out}/vacf${type}-${temp}.txt"
done
