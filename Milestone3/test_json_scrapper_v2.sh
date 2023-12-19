#!/bin/bash

ROOT_SAVE =cd

python json_scrapper_v2.py \
    -p_csv PATH_TO_CSV \
    -l_json LIST_JSON_FILES [LIST_JSON_FILES ...] \
    --shotGoalOnly 