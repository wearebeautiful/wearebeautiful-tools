#!/bin/bash

if [ "$#" -lt 4 ]; then
    echo "usage: make_bundle.sh [--invert] <low res len> <med res len> <src dir> <output dir>"
    exit 1
fi

if [ "$1" == "--invert" ]; then
    echo "invert yes"
    INVERT="--invert"
    shift
else
    echo "invert no"
    INVERT=""
fi

LRES=$1
MRES=$2
SRC=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $3`
DEST=`perl -e 'use Cwd "abs_path";print abs_path(shift)' $4`

echo "lres $LRES"
echo "mres $MRES"
echo "src $SRC"
echo "dest $DEST"

mkdir -p $DEST
docker rm -f mesh 
exec docker run -it --name mesh -v $SRC:/src -v $DEST:/dest wearebeautiful:mesh /code/wearebeautiful/bin/make_bundle.py $INVERT $LRES $MRES
