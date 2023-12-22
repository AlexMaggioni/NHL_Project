#!/bin/bash

docker build \
    -t ift6758/serving \
    --build-arg PORT=1234 \
    --progress=plain \
    --no-cache \
    -f Dockerfile.serving . 