#!/bin/bash
# Warning! Script executing simulations serially. Very slow and avoid doing this at ALL costs!
# You may have to explicitly set your OpenMMplugins directory!

lamvals=( 0.0 0.2 0.4 0.6 0.8 1.0 )

export OPENMM_PLUGIN_DIR=$SIREHOME/lib/plugins
for lam in "${lamvals[@]}"
do

echo "lambda is: " $lam
cd output
mkdir lambda-$lam
cd lambda-$lam
somd-freenrg -C ../../input/sim_min.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_1.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_2.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_3.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_4.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_5.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_npt_1.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_npt_2.cfg -l $lam -p CUDA
#rm -rf *dat
somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
#if [[ $lam == 0.0 ]]
#    then
#    cp ../../../../run001/free/output/lambda-1.0/sim_restart.s3 .
#    #somd-freenrg -C ../../input/sim_min.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_nvt_1.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_nvt_2.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_nvt_3.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_nvt_4.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_nvt_5.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_npt_1.cfg -l $lam -p CUDA
#    #rm -rf *.dat
#    #somd-freenrg -C ../../input/sim_npt_2.cfg -l $lam -p CUDA
#    #rm -rf *dat
#    somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
#else
#    last_lam = $(awk "BEGIN {print $lam - 0.2}")
#    cp ../lambda-$last_lam/sim_restart.s3 .
#    somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
#fi
cd ../../

done
