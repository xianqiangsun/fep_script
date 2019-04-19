"""
analyse_freenrg mbar --lam -i lam*/simfile.dat --temperature 298 -o out.dat --subsampling --overlap

generate temp file

fd, path = tempfile.mkstemp()
try:
    with os.fdopen(fd, 'w') as tmp:
        # do stuff with temp file
        tmp.write('stuff')
finally:
    os.remove(path)

"""

import os
import sys
import argparse
import numpy as np
import os

import tempfile




import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-sf', dest='simfile', default='gradients.dat')
parser.add_argument('-gf', dest='gradient_file', default='simfile.dat')
parser.add_argument('-os',dest='out_sim',default='sim.dat')
parser.add_argument("-tk", dest='number_to_keep', default=200, type=int, help="how many lines to keep")
parser.add_argument("-step", dest='steps', default=-1, type=int, help="how many lines to keep")
parser.add_argument("-skip", dest='skip', default=-1, type=int, help="how many lines to keep")
args = parser.parse_args()


def format_output(input_file, out_sim, keep_line_no, step, skip):
    keep_line_no = 0-keep_line_no
    a = np.loadtxt(input_file)[keep_line_no:]
    a = a[:step:skip]
    cmd = 'grep "#" '+input_file +' > '+out_sim
    os.system(cmd)
    f=open(out_sim,'ab')
    np.savetxt(f,a)
    f.close()

def list_folder(input):
    return [i for i in os.listdir(input) if os.path.isdir(i)]


def run_analysis(out_sim):
    for et in ["complex","solvated"]:
        os.chdir(et+"/output")
        cmd = "analyse_freenrg mbar --lam -i lam*/"+str(out_sim)+" --temperature 298 -o out.dat --subsampling --overlap"
        os.system(cmd)

if __name__ == "__main__":
    input_folder = os.path.abspath(args.input_folder)
    out_sim = args.out_sim
    all_dir = [i for i in os.listdir(input_folder) if os.path.isdir(i)]
    for ed in all_dir:
        os.chdir(ed)
        ed_dir = list_folder(ed)
        for et in ["complex","solvated"]:
            os.chdir(et+"/output")
            cmd = "analyse_freenrg mbar --lam -i lam*/"+str(out_sim)+" --temperature 298 -o out.dat --subsampling --overlap"
            os.system(cmd)
    os.chdir(input_folder)


















