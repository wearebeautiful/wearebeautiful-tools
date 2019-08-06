#!/bin/bash

docker rm -f mesh 
if [ "$#" -lt 3 ]; then
    docker run -it --name mesh wearebeautiful:mesh /code/wearebeautiful/bin/scale_mesh.py
    exit
fi

if [ "$1" == "--invert" ]; then
    echo "invert yes"
    INVERT="--invert"
    shift
else
    echo "invert no"
    INVERT=""
fi

LEN=$1
SRC_DIR=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $2`
DEST_DIR=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $3`

echo "source dir: $SRC_DIR"
echo "  dest dir: $DEST_DIR"
echo "target len: $LEN"

docker run -it --name mesh -v $SRC_DIR:/src -v $DEST_DIR:/dest wearebeautiful:mesh /code/wearebeautiful/bin/scale_mesh.py $INVERT $LEN /src /dest
