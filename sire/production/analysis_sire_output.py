"""

python analysis_sire_output,py -i ./sire -sf simfile.dat -p 60 -o energy.csv
analyse_freenrg mbar --lam -i lam*/simfile.dat --temperature 298 -o out.dat --subsampling --overlap -p 60

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
import pandas as pd
import numpy as np

import tempfile

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='./sire', help="the input file for the sire folder")
parser.add_argument('-sf', dest='simfile', default='gradients.dat')
parser.add_argument('-gf', dest='gradient_file', default='simfile.dat')
# parser.add_argument('-os', dest='out_sim', default='sim.dat')
# parser.add_argument("-tk", dest='number_to_keep', default=200, type=int, help="how many lines to keep")
# parser.add_argument("-step", dest='steps', default=-1, type=int, help="how many lines to keep")
# parser.add_argument("-skip", dest='skip', default=-1, type=int, help="how many lines to keep")
parser.add_argument("-p", dest='percent', default=60, type=int, help="how many percents of data to keep")
parser.add_argument("-o", dest='output_vds', default="energy.csv", type=str, help="the output energy file")

args = parser.parse_args()

'''
def format_output(input_file, out_sim, keep_line_no, step, skip):
    keep_line_no = 0 - keep_line_no
    a = np.loadtxt(input_file)[keep_line_no:]
    a = a[:step:skip]
    cmd = 'grep "#" ' + input_file + ' > ' + out_sim
    os.system(cmd)
    f = open(out_sim, 'ab')
    np.savetxt(f, a)
    f.close()
'''


def list_folder(input):
    return [i for i in os.listdir(input) if os.path.isdir(i)]


def run_analysis(output_file):
    a = open(output_file, 'r')
    all_lines = [i.rstrip() for i in a.readlines()]
    ti = float(all_lines[-1])
    mbar = float(all_lines[-3].split(",")[0])
    mbar_sd = float(all_lines[-3].split(",")[1])
    return ti, mbar, mbar_sd


if __name__ == "__main__":
    input_folder = os.path.abspath(args.input_folder)
    out_sim = args.out_sim
    all_dir = [input_folder + "/" + i for i in os.listdir(input_folder) if os.path.isdir(input_folder + "/" + i)]
    all_energy_dic = {}
    for ed in all_dir:
        df_mbar = pd.DataFrame(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
                               columns=['vdw', 'charge', 'onestep', 'decharge', 'recharge'],
                               index=["complex", "solvated"])
        df_mbar_error = pd.DataFrame(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
                                     columns=['vdw', 'charge', 'onestep', 'decharge', 'recharge'],
                                     index=["complex", "solvated"])
        df_ti = pd.DataFrame(np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
                             columns=['vdw', 'charge', 'onestep', 'decharge', 'recharge'],
                             index=["complex", "solvated"])
        os.chdir(ed)
        ed_dir = list_folder(ed)
        transformation_name = ed.split("/")[-1]

        for ed in ed_dir:
            for et in ["complex", "solvated"]:
                os.chdir(et + "/output")
                output_file = "out_" + str(args.percent) + ".dat"
                cmd = "analyse_freenrg mbar --lam -i lam*/" + str(
                    out_sim) + " --temperature 298 -o " + output_file + " --subsampling --overlap -p " + args.percent
                os.system(cmd)
                ti_value, mbar_value, mbar_sd = run_analysis(output_file=output_file)
                df_mbar[ed][et] = mbar_value
                df_mbar_error[ed][et] = mbar_sd
                df_ti[ed][et] = ti_value

        df_mbar["sum"] = df_mbar.sum(axis=1)
        df_mbar_error["sum"] = df_mbar_error.sum(axis=1)
        df_ti["sum"] = df_ti.sum(axis=1)
        mbar_energy = df_mbar["sum"]["solvated"] - df_mbar["sum"]["complex"]
        ti_energy = df_ti["sum"]["solvated"] - df_ti["sum"]["complex"]
        all_energy_dic[transformation_name] = [mbar_energy, ti_energy]
    os.chdir(input_folder)
    a = pd.DataFrame(all_energy_dic, index=["ti (kcal/mol)", "mbar (kcal/mol)"]).transpose()
    a.to_csv(args.output_csv)
