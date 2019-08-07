#!/bin/bash

docker rm -f mesh 
if [ "$#" -lt 1 ]; then
    docker run -it --name mesh wearebeautiful:mesh /code/wearebeautiful/bin/dump_mesh.py
    exit
fi

SRC_PATH=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $1`
SRC_DIR=`dirname $SRC_PATH`
SRC_FILE=`basename $SRC_PATH`

docker run -it --name mesh -v $SRC_DIR:/src wearebeautiful:mesh /code/wearebeautiful/bin/dump_mesh.py $SRC_FILE
