#!/usr/bin/bash

dtype=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t | --type)
            ice_type="$2"
            shift 2
            ;;
        -s | --startstop)
            start="$2"
            stop="$3"
            shift 3
            ;;
        -d | --data)
            shift
            while [[ $# -gt 1 ]]; do
                dtype+=("$1")
                shift
            done
            ;;
        -* | --*)
            echo "unknown option: $1"
            exit 1
            ;;
        *)
            thermo_file="$1"
            shift
            ;;
    esac
done

out="plots/hmsdvar.txt"
./data_analysis.py -d -i "$ice_type" -s "${start},${stop}" -k "${dtype[@]}" "$thermo_file" > "$out"
