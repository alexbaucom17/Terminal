#!/usr/bin/env bash
echo "Run Match"
starterAlgo=$PWD/algos/starter-algo
myAlgo=$PWD/algos/my-algo-v1

algo1=${1:-${myAlgo}}
algo1=${algo1%/}
algo2=${2:-${starterAlgo}}
algo2=${algo2%/}

echo "P1: ${algo1}"
echo "P2: ${algo2}"
echo "Starting Match: ${algo1} vs. ${algo2}"
java -jar engine.jar work ${algo1}/run.sh ${algo2}/run.sh
