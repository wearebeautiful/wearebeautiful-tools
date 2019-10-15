#!/bin/bash

docker rm -f mesh 
if [ "$#" -lt 1 ]; then
    echo "Run any .py script in this dir inside of docker -- local dir is mounted into container"
    exit
fi

docker run -it --name mesh -v `pwd`:/code/wab wearebeautiful:mesh python3 $@
if [ "$?" -eq 137 ]; then
    echo "Error: out of memory. give docker more ram!"
    exit
fi
