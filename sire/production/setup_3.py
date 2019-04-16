#!/usr/bin/python
'''
    File name: setup.py
    Author: Antonia Mey, Julien Michel
    Python Version: 2.7 or 3.5

    #
    Prepares input files for a somd simulation of the somd tutorial using:
    all _perturbations folders in the input directory
    the protocol in sim.cfg
    the lambdas schedule in lambdas.schedule
    the submission syntax script sub-somd.sh
    python setup_3.py ../FESetup/_perturbations/sire/ 
'''
# Imports
import os, sys
import os.path
from os import path

# reading from command line
try:
    indir = sys.argv[1]
except IndexError:
    print ("Usage is: python setup.py path/to/FESEtup/_perturbations")
    sys.exit(-1)

a = os.walk(indir)
dirlist = a.__next__()[1]
print ("-------------------------------------------------------------------")
print ("----|Setup.py for Sire alchemical free energy simulation setup|----")
print ("-------------------------------------------------------------------")
print ('\n')
print ("Found the following pertubrations:")
for d in dirlist:
    print (d)
print ('----------------------------------')
print ('\n')
print ('Now doing the actual setting up:')
print ('--------------------------------')
curr_work_dir = os.getcwd()


def check_file_exist(filename):
    '''
    :param filename: the filename in the folder
    :return: whether the file exist or not
    '''
    return path.exist(filename)


def charge_file(input_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
    """
    a = open(input_file, 'r')
    all_lines = []
    for l in a.readlines():
        all_lines.append(l)
    return all_lines

def copy_files(input_file, output_file):
    '''
    :param input_file:
    :param output_file:
    :return:
    '''
    cmd = "cp "+input_file+' '+output_file
    os.system(cmd)


'''
MORPH.decharge.pert
MORPH.recharge.pert
'''

for directory in dirlist:
    inputfolder = os.path.join(indir, directory)
    elems = inputfolder.split("/")
    inputfolder = os.path.abspath(inputfolder)
    #define all the input files

    solvated_parm7 = inputfolder+'/solvated.parm7'
    pert = elems[-2]
    print ("Setting up %s ... " % elems[-1])
    basedir = os.getcwd()
    if not os.path.exists(pert):
        cmd = "mkdir %s" % pert
        os.system(cmd)

    os.chdir(pert)
    files = os.listdir(os.getcwd())
    cmd = "mkdir %s" % directory
    os.system(cmd)
    os.chdir(directory)
    files = os.listdir(os.getcwd())
    index = 1
    for f in files:
        if f.find("run") > -1:
            index = index + 1
    runfolder = "run%003d" % index
    cmd = "mkdir %s" % runfolder
    os.system(cmd)
    if index > 1:
        print ("Previous run folders exist, files set up in %s " % runfolder)

    os.chdir(runfolder)
    '''For each calculation we need
    SYSTEM.pdb SYSTEM.top SYSTEM.crd
    MORPH.onestep.pert MORPH.onestep.flex
    sim.cfg
    somd-freenrg.sh (that one makes subfolders according to lamba values)'''

    # Ligand in solvant setup (charge)

    files = os.listdir(inputfolder)
    match = False
    for f in files:
        if f.find("solvated") > -1:
            match = True
            break
    if match:
        cmd = "mkdir free"
        os.system(cmd)
        cmd = "mkdir free/input"
        os.system(cmd)
        cmd = "mkdir free/output"
        os.system(cmd)
        """
        copy the input files for the run0001 file, which is the decharge step
        """

        copy_files(inputfolder)

        cmds = ["cp %s/solvated/solvated.parm7 free/input/SYSTEM.top" % inputfolder,
                "cp %s/solvated/solvated.pdb free/input/SYSTEM.pdb" % inputfolder,
                "cp %s/solvated/solvated.rst7 free/input/SYSTEM.crd" % inputfolder,
                # "cp %s/MORPH.vdw.pert free/input/MORPH.vdw.pert" % inputfolder,
                "cp %s/ligand.flex free/input/MORPH.flex" % inputfolder,
                "cp %s/scripts/sim_*.cfg free/input/" % basedir,
                "cp %s/scripts/cluster.sh free/" % basedir,
                "cp %s/scripts/serial_charge.sh free/serial.sh" % basedir
                ]
        for cmd in cmds:
            os.system(cmd)


    # Ligand bound to protein setup (charge)
    match = False
    for f in files:
        if f.find("complex") > -1:
            match = True
            break
    if match:
        cmd = "mkdir bound"
        os.system(cmd)
        cmd = "mkdir bound/input"
        os.system(cmd)
        cmd = "mkdir bound/output"
        os.system(cmd)
        cmds = ["cp %s/complex/solvated.parm7 bound/input/SYSTEM.top" % inputfolder,
                "cp %s/complex/solvated.pdb bound/input/SYSTEM.pdb" % inputfolder,
                "cp %s/complex/solvated.rst7 bound/input/SYSTEM.crd" % inputfolder,
                "cp %s/MORPH.charge.pert bound/input/MORPH.pert" % inputfolder,
                # "cp %s/MORPH.vdw.pert bound/input/MORPH.vdw.pert" % inputfolder,
                "cp %s/ligand.flex bound/input/MORPH.flex" % inputfolder,
                "cp %s/scripts/sim_*.cfg bound/input/" % basedir,
                "cp %s/scripts/cluster.sh bound/" % basedir,
                "cp %s/scripts/serial_charge.sh bound/serial.sh" % basedir
                ]
        for cmd in cmds:
            os.system(cmd)
    # Ligand in solvant setup (charge)
    os.chdir("../")
    index += 1
    runfolder = "run%003d" % index
    cmd = "mkdir %s" % runfolder
    os.system(cmd)
    os.chdir(runfolder)
    match = False
    for f in files:
        if f.find("solvated") > -1:
            match = True
            break
    if match:
        cmd = "mkdir free"
        os.system(cmd)
        cmd = "mkdir free/input"
        os.system(cmd)
        cmd = "mkdir free/output"
        os.system(cmd)
        cmds = ["cp %s/solvated/solvated.parm7 free/input/SYSTEM.top" % inputfolder,
                "cp %s/solvated/solvated.pdb free/input/SYSTEM.pdb" % inputfolder,
                "cp %s/solvated/solvated.rst7 free/input/SYSTEM.crd" % inputfolder,
                # "cp %s/MORPH.charge.pert free/input/MORPH.charge.pert" % inputfolder,
                "cp %s/MORPH.vdw.pert free/input/MORPH.pert" % inputfolder,
                "cp %s/ligand.flex free/input/MORPH.flex" % inputfolder,
                "cp %s/scripts/sim_*.cfg free/input/" % basedir,
                "cp %s/scripts/cluster.sh free/" % basedir,
                "cp %s/scripts/serial_vdw_solvated.sh free/serial.sh" % basedir
                ]
        for cmd in cmds:
            os.system(cmd)

    # Ligand bound to protein setup(vdw)
    match = False
    for f in files:
        if f.find("complex") > -1:
            match = True
            break
    if match:
        cmd = "mkdir bound"
        os.system(cmd)
        cmd = "mkdir bound/input"
        os.system(cmd)
        cmd = "mkdir bound/output"
        os.system(cmd)
        cmds = ["cp %s/complex/solvated.parm7 bound/input/SYSTEM.top" % inputfolder,
                "cp %s/complex/solvated.pdb bound/input/SYSTEM.pdb" % inputfolder,
                "cp %s/complex/solvated.rst7 bound/input/SYSTEM.crd" % inputfolder,
                # "cp %s/MORPH.charge.pert bound/input/MORPH.charge.pert" % inputfolder,
                "cp %s/MORPH.vdw.pert bound/input/MORPH.pert" % inputfolder,
                "cp %s/ligand.flex bound/input/MORPH.flex" % inputfolder,
                "cp %s/scripts/sim_*.cfg bound/input/" % basedir,
                "cp %s/scripts/cluster.sh bound/" % basedir,
                "cp %s/scripts/serial_vdw_complex.sh bound/serial.sh" % basedir
                ]
        for cmd in cmds:
            os.system(cmd)
    os.chdir(curr_work_dir)
