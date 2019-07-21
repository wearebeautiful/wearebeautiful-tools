#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "usage: make_bundle.sh <low res len> <med res len> <src dir> <output dir>"
    exit
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
docker run -it --name mesh -v $SRC:/src -v $DEST:/dest wearebeautiful:mesh /code/wearebeautiful/bin/make_bundle.py $LRES $MRES
