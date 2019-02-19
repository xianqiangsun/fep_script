#!/bin/bash

for i in benzol~o-xylene o-xylene~benzol 
do
    cd sire/$i/run001/free/output
    sbatch ../cluster.sh
    cd ../../bound/output
    sbatch ../cluster.sh
    cd ../../../../../

done
