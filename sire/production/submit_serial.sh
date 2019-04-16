#!/bin/bash

for i in $(ls ../sire);
do
    echo $i;
    cd $i;
    for j in $(ls .);
    do
        echo $j;
        cd $j;
        for k in $(ls .);
        do
            echo $k;
            cd $k;
            sh serial.sh;
            cd ../;
        done
    cd ../;
    done
cd ../;
done



