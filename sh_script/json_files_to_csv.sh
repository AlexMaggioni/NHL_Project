#!/bin/bash

# Verifying that the arguments are int and not empty and greater than each other
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <YEAR_1> <YEAR_2>"
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 <YEAR_1> <YEAR_2>"
    exit 1
fi

if [ "$1" -gt "$2" ]; then
    echo "Usage: $0 <YEAR_1> <YEAR_2>"
    exit 1
fi

YEAR_1=$1
YEAR_2=$2

BASE_DIR_PARENT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR_PARENT=$(dirname "$BASE_DIR_PARENT")

PATH_TO_SCRIPT=$BASE_DIR_PARENT/Milestone1/json_scrapper.py

LAST_COMMIT_ID=$(git log -1 --pretty=format:"%h" "$PATH_TO_SCRIPT")

printf '\t\t LAST COMMIT ID: %s \n\n' "$LAST_COMMIT_ID"
printf '\t\t RUNNING THE SCRIPT : %s \n\n' "$PATH_TO_SCRIPT"

# Running the script

# Relative from the ENV var DATA_FOLDER in .env file 
ARG1="json_scrapper_output/raw_data_${YEAR_1}_${YEAR_2}_${LAST_COMMIT_ID}.csv"
ARG2=$(seq -s ' ' "$YEAR_1" "$YEAR_2")

printf '\t\t --path_to_csv: %s \n\n' "$ARG1"
printf '\t\t --years: %s \n\n' "$ARG2"

python "$PATH_TO_SCRIPT" \
    --path_to_csv "$ARG1" \
    --years $ARG2