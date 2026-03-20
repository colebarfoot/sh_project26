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
            ice_type="$2"
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

if [[ -z "$ice_type" ]]; then
    echo "type not specified"
    exit 1
fi
if [[ "$ice_type" == "7p" ]]; then ice_type="7"; fi

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
for thermo_file in "$indir"/parsed-isotherm"$ice_type"-*; do
    temp="$(basename "$thermo_file")"
    temp="${temp#parsed-isotherm"$ice_type"-}"
    temp="${temp#*-}"
    temp="${temp%-*}"
    ./data_analysis.py -i "$ice_type" --startstop 2990000,3000000 --phonon "$thermo_file" \
        > "${out}/vacf${ice_type}-${temp}.txt"
done
