#!/bin/bash

if [ "$#" -lt 3 ]; then
    echo "usage: scale_mesh.sh <len> <src dir> <dest dir>"
    exit
fi

SRC_DIR=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $2`
echo "source dir: $SRC_DIR"

DEST_DIR=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $3`
echo "  dest dir: $DEST_DIR"

LEN=$1
echo "target len: $LEN"

docker rm -f mesh 
docker run -it --name mesh -v $SRC_DIR:/src -v $DEST_DIR:/dest wearebeautiful:mesh /code/wearebeautiful/bin/scale_mesh.py $LEN /src /dest
