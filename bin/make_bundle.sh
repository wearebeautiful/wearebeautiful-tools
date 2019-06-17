#!/bin/bash

PRINT=$1
SURFACE=$2
LRES=$3
MRES=$4
MANIFEST=$5
cd $6
DEST=`pwd`
cd -
echo "$DEST"

docker rm -f mesh 
docker build -t wearebeautiful:mesh .
docker run -it --name mesh -v `pwd`:/models -v $DEST:/out wearebeautiful:mesh /code/make_bundle.py $PRINT $SURFACE $LRES $MRES $MANIFEST $DEST
