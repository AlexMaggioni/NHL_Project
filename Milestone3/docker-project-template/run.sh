#!/bin/bash

docker run --rm \
    --env COMET_API_KEY="$COMET_API_KEY" \
    -p '1234:1234' \
    ift6758/serving