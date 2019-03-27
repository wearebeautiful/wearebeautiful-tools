#!/bin/bash

docker run -d \
    --expose 3031 \
    --name ismaydeadyet-co-uk-beta \
    -v /home/website/ismaydeadyet.co.uk:/code/ismaydeadyet.co.uk\
    --env "VIRTUAL_HOST=ismaydeadyet.co.uk" \
    --env "LETSENCRYPT_HOST=ismaydeadyet.co.uk" \
    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
    --network=website-network \
    ismaydeadyet-co-uk-web:beta
