#!/bin/bash

if [ "$1" = "build" ]
then
    docker build -f Dockerfile -t wearebeautiful:tools .
    exit
fi

if [ "$1" = "up" ]
then
    docker run -d --rm --name wab-tools -v `pwd`:/code/wab wearebeautiful:tools python3 wearebeautiful/fussy_is_forever.py
    exit
fi

if [ "$1" = "down" ]
then
    docker rm -f wab-tools
    exit
fi

docker exec -it wab-tools python3 $@
if [ "$?" -eq 137 ]; then
    echo "Error: out of memory. give docker more ram!"
    exit
fi
