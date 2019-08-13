#!/bin/bash

docker rm -f mesh 
if [ "$#" -lt 2 ]; then
    docker run -it --name mesh wearebeautiful:mesh /code/wearebeautiful/bin/asplode_mesh.py
    exit
fi

SCALE=$1
SRC_PATH=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $2`
SRC_DIR=`dirname $SRC_PATH`
SRC_FILE=`basename $SRC_PATH`

echo "     scale: $SCALE"
echo "source dir: $SRC_DIR"
echo "   src dir: $SRC_FILE"

docker run -it --name mesh -v $SRC_DIR:/src wearebeautiful:mesh /code/wearebeautiful/bin/asplode_mesh.py $SCALE $SRC_FILE
