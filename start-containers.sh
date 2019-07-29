#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run \
    --name wab-redis \
    --network=website-network \
    -d redis

docker run -d \
    --expose 3031 \
    --name wearebeautiful.info-beta \
    -v wab-bundles:/code/wearebeautiful.info/static/bundle \
    -v $SRC_DIR/admin/nginx/vhost.d:/etc/nginx/vhost.d:ro \
    --env "VIRTUAL_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
    --network=website-network \
    wearebeautiful.info:beta
