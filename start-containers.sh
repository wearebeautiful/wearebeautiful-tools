#!/bin/bash

docker run -d \
    --expose 3031 \
    --name wearebeautiful.info-beta \
    -v /home/website/wearebeautiful.info:/code/wearebeautiful.info\
    --env "VIRTUAL_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
    --network=website-network \
    wearebeautiful.info:beta
