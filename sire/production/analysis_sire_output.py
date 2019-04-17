"""
analyse_freenrg mbar --lam -i lam*/simfile.dat --temperature 298 -o out.dat --subsampling --overlap
"""

import os
import sys
import argparse

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-s', dest='script_folder', default="script", help="the input script file for the sire folder")
parser.add_argument('-o', dest='output_folder', default='sire')
parser.add_argument('-sub', dest='submit', default='submit.sh')
parser.add_argument('-c', dest='convert', default=True)
args = parser.parse_args()

