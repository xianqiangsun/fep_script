#!/bin/bash
# Warning! Script executing simulations serially. Very slow and avoid doing this at ALL costs!
# You may have to explicitly set your OpenMMplugins directory!


lamvals=( 0.0 0.1 0.2 0.3 0.4 0.6 0.7 0.8 0.9 1.0 )

export OPENMM_PLUGIN_DIR=$SIREHOME/lib/plugins

cd output
mkdir lambda-0.5
cd lambda-0.5
somd-freenrg -C ../../input/sim_min.cfg -l $lam -p CUDA
#rm -rf *.dat
somd-freenrg -C ../../input/sim_nvt_1.cfg -l $lam -p CUDA
rm -rf *.dat
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
cp sim_restart.s3 sim_restart.s3.others
rm -rf *dat
somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
cd ../

for lam in "${lamvals[@]}"
do

echo "lambda is: " $lam

mkdir lambda-$lam
cd lambda-$lam
cp ../lambda-0.5/sim_restart.s3.others sim_restart.s3

#somd-freenrg -C ../../input/sim_min.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_nvt_1.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_nvt_2.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_nvt_3.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_nvt_4.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_nvt_5.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_npt_1.cfg -l $lam -p CUDA
#rm -rf *.dat
#somd-freenrg -C ../../input/sim_npt_2.cfg -l $lam -p CUDA
#rm -rf *dat
somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
cd ..

done
