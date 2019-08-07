#!/bin/bash

docker rm -f mesh 
if [ "$#" -lt 2 ]; then
    docker run -it --name mesh wearebeautiful:mesh /code/wearebeautiful/bin/invert_mesh.py
    exit
fi

SRC_PATH=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $1`
DEST_PATH=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $2`

SRC_DIR=`dirname $SRC_PATH`
SRC_FILE=`basename $SRC_PATH`
DEST_DIR=`dirname $DEST_PATH`
DEST_FILE=`basename $DEST_PATH`

echo " source dir: $SRC_DIR"
echo "source file: $SRC_FILE"
echo "   dest dir: $DEST_DIR"
echo "  dest file: $DEST_FILE"

docker run -it --name mesh -v $SRC_DIR:/src -v $DEST_DIR:/dest wearebeautiful:mesh /code/wearebeautiful/bin/invert_mesh.py $SRC_FILE $DEST_FILE
