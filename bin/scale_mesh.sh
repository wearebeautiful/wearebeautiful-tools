#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "usage: scale_mesh.sh <src file> <dest file> <len>"
    exit
fi

IN_FILE=$1
OUT_FILE=$2
RES=$3

docker rm -f mesh 
#docker run -it --name mesh -v `pwd`:/code/vol wearebeautiful:mesh bash
docker run -it --name mesh -v `pwd`:/code/vol wearebeautiful:mesh /code/scale_mesh.py /code/vol/$IN_FILE /code/vol/$OUT_FILE $RES
