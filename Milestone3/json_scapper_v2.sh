#!/bin/bash

PATH_OUTPUT_CSV="v2_api/json_scrapper_output/scrapped_1.csv" # CONCATENATE TO DATA_FOLDER ENV VAR IN .env

ROOT_JSON_FILES_TO_SCRAPE='/home/lolo/Documents/UDEM_courses/session_automne_2023/data_science/projet_NHL_repo/IFT6758_NHL/data/v2_api/raw_json_files'
JSON_FILES_TO_SCRAPE=$(realpath ${ROOT_JSON_FILES_TO_SCRAPE}/*.json --zero | xargs -0 echo)

python /home/lolo/Documents/UDEM_courses/session_automne_2023/data_science/projet_NHL_repo/IFT6758_NHL/Milestone3/json_scrapper_v2.py \
    --path_to_csv "$PATH_OUTPUT_CSV" \
    --json_files "$JSON_FILES_TO_SCRAPE"\
    --shotGoalOnly 
    # --comet_dl