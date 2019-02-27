#!/bin/sh
#
# Method 1: setup for a fully dual-topology side chain residue
#

tleap=$AMBERHOME/bin/tleap
basedir=leap


$tleap -f - <<_EOF
# load the AMBER force fields
source leaprc.ff14SB
source leaprc.gaff
loadAmberParams frcmod.ionsjc_tip3p

# load force field parameters for BNZ
loadoff $basedir/benz.lib

# load the coordinates and create the systems
ligand = loadpdb $basedir/bnz.pdb
m1 = loadpdb $basedir/181L_mod.pdb
m2 = loadpdb $basedir/181L_A99V.pdb
w = loadpdb $basedir/water_ions.pdb

protein = combine {m1 m2 w}
complex = combine {m1 m2 ligand w}

set default nocenter on

# create protein in solution
setBox protein vdw {32.71 31.46 43.84}
savepdb protein protein.pdb
saveamberparm protein protein.parm7 protein.rst7

# create complex in solution
setBox complex vdw {32.71 31.46 43.84}
savepdb complex complex.pdb
saveamberparm complex complex.parm7 complex.rst7

quit
_EOF
