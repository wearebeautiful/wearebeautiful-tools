#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "usage: make_bundle.sh <src dir> <low res len> <med res len> <output dir>"
    exit
fi

cd $1
SRC=`pwd`
cd -
LRES=$2
MRES=$3
cd $4
DEST=`pwd`
cd -

echo "src $SRC"
echo "lres $LRES"
echo "mres $MRES"
echo "dest $DEST"

mkdir -p $DEST
docker rm -f mesh 
docker run -it --name mesh -v `pwd`:/models -v $SRC:/src -v $DEST:/dest wearebeautiful:mesh /code/make_bundle.py $LRES $MRES
