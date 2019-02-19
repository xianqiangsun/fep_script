#!/bin/bash

for i in 1~r  2~r  3~r  4~r  5~r  6~r  8~r  9~r  r~1  r~2  r~3  r~4  r~5  r~6  r~8  r~9;
do
    cd sire/$i/run000/bound/output
    sh ../serial.sh
    cd ../../free/output
    sh ../serial.sh
    cd ../../../../../
    cd sire/$i/run001/bound/output
    sh ../serial.sh
    cd ../../free/output
    sh ../serial.sh
    cd ../../../../../
    cd sire/$i/run002/bound/output
    sh ../serial.sh
    cd ../../free/output
    sh ../serial.sh
    cd ../../../../../
    
done
