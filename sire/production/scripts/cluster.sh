#!/bin/bash
#You may again want to adapt the OPENMM_PLUGIN_DIR environment 
#variable below to the correct path
#SBATCH -o somdtutorial-%A.%a.out
#SBATCH -p GTX
#SBATCH -n 1
#SBATCH --gres=gpu:1
#SBATCH --time 24:00:00
#SBATCH --array=0-8

echo "CUDA DEVICES:" $CUDA_VISIBLE_DEVICES

lamvals=( 0.0000 0.1250 0.2500 0.3750 0.5000 0.6250 0.7500 0.8750 1.0000 )
lam=${lamvals[SLURM_ARRAY_TASK_ID]}

sleep 5

echo "lambda is: " $lam

mkdir lambda-$lam
cd lambda-$lam

#export OPENMM_PLUGIN_DIR=/home/user/sire.app/lib/plugins/

somd-freenrg -C ../../input/sim.cfg -l $lam -p CUDA
cd ..

wait
