#!/bin/bash

if [ ! -d ".ve" ]; then
    virtualenv -p python3 .ve
    source .ve/bin/activate
    pip3 install -r requirements.txt
else
    source .ve/bin/activate
fi

# Start the redis container 
CHECK_REDIS=`docker ps | grep wab-redis`
if [ -z "$CHECK_REDIS" ]; then
    echo "stop redis, if it happens to be stopped"
    docker rm -f wab-redis
    echo "start redis"
    docker run --name wab-redis -p 6379:6379 -d redis
fi

# set the env
export FLASK_APP=wearebeautiful/app.py
export FLAK_ENV=development
export FLASK_DEBUG=1
export FLASK_RUN_HOST=0.0.0.0

# run it!
flask run
