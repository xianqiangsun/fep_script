#!/bin/bash
# Warning! Script executing simulations serially. Very slow and avoid doing this at ALL costs!
# You may have to explicitly set your OpenMMplugins directory!

#export gpu
export OPENMM_PLUGIN_DIR=$SIREHOME/lib/plugins
cd output

lamvals=( 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 )


for lam in "${lamvals[@]}"
    do
    echo "lambda is: " $lam
    mkdir lambda-$lam
    cd lambda-$lam
    somd-freenrg -C ../../input/sim_min.cfg -l $lam -p CUDA
    somd-freenrg -C ../../input/sim_nvt_1.cfg -l $lam -p CUDA
    somd-freenrg -C ../../input/sim_npt_2.cfg -l $lam -p CUDA
    somd-freenrg -C ../../input/sim_md.cfg -l $lam -p CUDA
    cd ..
    done

