"""
application
python sire_setup_two_step.py -i ../_perturbations/sire -s scripts -o sire -c false -sub submit,sh
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

submit_lines = """
#!/bin/bash

for i in $(ls -d */);
do
    echo $i;
    cd $i;
    for j in $(ls -d */);
    do
        echo $j;
        cd $j;
        for k in $(ls -d */);
        do
            echo $k;
            cd $k;
            sh serial.sh;
            cd ../;
        done
    cd ../;
    done
cd ../;
done
"""

def write_file(all_lines, output_file):
    a = open(output_file, "w")
    for el in all_lines:
        a.writelines(el)
    a.close()


def make_directory(folder):
    '''
    :param folder:
    :return: make the directory if it is not exist
    '''
    try:
        os.stat(folder)
    except:
        os.mkdir(folder)


def vdw_name_LJ(vdw_file):
    a = open(vdw_file, 'r')
    all_lines = []
    atom_lj_dic = {}
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:6] == "name":
            initial_LJ = all_lines[el_no + 3].split()[1:]
            final_LJ = all_lines[el_no + 4].split()[1:]
            atom_lj_dic[el.split()[1]] = [initial_LJ, final_LJ]
    return atom_lj_dic
'''
#======================================================
#not converting the files anymore
def decharge_file(input_file, output_file, vdw_file):
    """
    #:param input_file: input file for the charge to generate decharge
    #:return: the de charged file
    """
    all_lj_dic = vdw_name_LJ(vdw_file)
    a = open(input_file, 'r')
    out_f = open(output_file, "w")
    all_lines = []
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:14] == "final_charge":
            all_lines[el_no] = "     final_charge    0.00000\n"
            atom_name = all_lines[el_no - 6].split()[-1]
            lj = all_lj_dic[atom_name]
            all_lines[el_no - 2] = "        initial_LJ      " + lj[0][0] + '  ' + lj[0][1]
            all_lines[el_no - 2] = "        final_LJ        " + lj[0][0] + '  ' + lj[0][1]
    for el in all_lines:
        out_f.write(el)


def recharge_file(input_file, output_file):
    """
    #:param input_file: input file for the charge to generate decharge
    #:return: the de charged file
    """
    a = open(input_file, 'r')
    out_f = open(output_file, "w")
    for l in a.readlines():
        if l[2:16] == "initial_charge":
            l = "     initial_charge  0.00000\n"
            out_f.write(l)
        else:
            out_f.write(l)


def pert_vdw_file(input_file, output_file):
    """
    #:param input_file: input file for the charge to generate decharge
    #:return: the de charged file
    """
    a = open(input_file, 'r')
    out_f = open(output_file, "w")
    for l in a.readlines():
        if l[2:16] == "initial_charge":
            l = "     initial_charge  0.00000\n"
            out_f.write(l)
        elif l[2:14] == "final_charge":
            l = "     final_charge    0.00000\n"
            out_f.write(l)
        else:
            out_f.write(l)


def solvated_decharge(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    #:param each_pert_abs: the absolute path of each pert generated from FESetup
    #:param script_folder: the input script and simulation configuration files
    #:param charge_state: whether the ligand is recharge or decharged
    #:param each_pert_output_run: the output run output folder
    #:return:
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/solvated/solvated.parm7 free/input/SYSTEM.top" % each_pert_abs,
            "cp %s/solvated/solvated.pdb free/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/solvated/solvated.rst7 free/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex free/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg free/input/" % script_folder,
            "cp %s/cluster.sh free/" % script_folder,
            "cp %s/serial_decharge.sh free/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.decharge.pert free/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        decharge_file_output = "free/input/MORPH.pert"
        decharge_file(charge_file_input, decharge_file_output, vdw_file_input)


def complex_decharge(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    #:param each_pert_abs: the absolute path of each pert generated from FESetup
    #:param script_folder: the input script and simulation configuration files
    #:param charge_state: whether the ligand is recharge or decharged
    #:param each_pert_output_run: the output run output folder
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/complex/solvated.parm7 bound/input/SYSTEM.top" % each_pert_abs,
            "cp %s/complex/solvated.pdb bound/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/complex/solvated.rst7 bound/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex bound/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg bound/input/" % script_folder,
            "cp %s/cluster.sh bound/" % script_folder,
            "cp %s/serial_decharge.sh bound/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.decharge.pert bound/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        decharge_file_output = "bound/input/MORPH.pert"
        decharge_file(charge_file_input, decharge_file_output)


def solvated_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    :param each_pert_abs: the absolute path of each pert generated from FESetup
    :param script_folder: the input script and simulation configuration files
    :param charge_state: whether the ligand is recharge or decharged
    :param each_pert_output_run: the output run output folder
    :return:
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/solvated/solvated.parm7 free/input/SYSTEM.top" % each_pert_abs,
            "cp %s/solvated/solvated.pdb free/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/solvated/solvated.rst7 free/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex free/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg free/input/" % script_folder,
            "cp %s/cluster.sh free/" % script_folder,
            "cp %s/serial_vdw_solvated.sh free/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.vdw.pert free/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        vdw_file_output = "free/input/MORPH.pert"
        pert_vdw_file(vdw_file_input, vdw_file_output)


def complex_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    :param each_pert_abs: the absolute path of each pert generated from FESetup
    :param script_folder: the input script and simulation configuration files
    :param charge_state: whether the ligand is recharge or decharged
    :param each_pert_output_run: the output run output folder
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/complex/solvated.parm7 bound/input/SYSTEM.top" % each_pert_abs,
            "cp %s/complex/solvated.pdb bound/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/complex/solvated.rst7 bound/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex bound/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg bound/input/" % script_folder,
            "cp %s/cluster.sh bound/" % script_folder,
            "cp %s/serial_vdw_complex.sh bound/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.vdw.pert bound/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        vdw_file_output = "bound/input/MORPH.pert"
        pert_vdw_file(vdw_file_input, vdw_file_output)


def solvated_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    :param each_pert_abs: the absolute path of each pert generated from FESetup
    :param script_folder: the input script and simulation configuration files
    :param charge_state: whether the ligand is recharge or decharged
    :param each_pert_output_run: the output run output folder
    :return:
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/solvated/solvated.parm7 free/input/SYSTEM.top" % each_pert_abs,
            "cp %s/solvated/solvated.pdb free/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/solvated/solvated.rst7 free/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex free/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg free/input/" % script_folder,
            "cp %s/cluster.sh free/" % script_folder,
            "cp %s/serial_recharge_solvated.sh free/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.recharge.pert free/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        recharge_file_output = "free/input/MORPH.pert"
        recharge_file(charge_file_input, recharge_file_output)


def complex_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run):
    """
    :param each_pert_abs: the absolute path of each pert generated from FESetup
    :param script_folder: the input script and simulation configuration files
    :param charge_state: whether the ligand is recharge or decharged
    :param each_pert_output_run: the output run output folder
    """
    os.chdir(each_pert_output_run)
    cmds = ["cp %s/complex/solvated.parm7 bound/input/SYSTEM.top" % each_pert_abs,
            "cp %s/complex/solvated.pdb bound/input/SYSTEM.pdb" % each_pert_abs,
            "cp %s/complex/solvated.rst7 bound/input/SYSTEM.crd" % each_pert_abs,
            "cp %s/ligand.flex bound/input/MORPH.flex" % each_pert_abs,
            "cp %s/sim_*.cfg bound/input/" % script_folder,
            "cp %s/cluster.sh bound/" % script_folder,
            "cp %s/serial_recharge_complex.sh bound/serial.sh" % script_folder
            ]
    for cmd in cmds:
        os.system(cmd)
    if charge_state:
        cmd = "cp %s/MORPH.recharge.pert bound/input/MORPH.pert" % each_pert_abs
        os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        recharge_file_output = "bound/input/MORPH.pert"
        decharge_file(charge_file_input, recharge_file_output)
'''

def copy_file(each_pert_abs, solvation_complex, calculation_format, script_folder, each_pert_output_run):
    """
    :param each_pert_abs: the abslute path of each pert
    :param solvation_complex: is the simulation a complex or solvation
    :param calculation_format: recharge, charge, vdw, onestep
    :param script_folder: the folder of the script
    :param each_pert_output_run: the output folder location
    :return:
    """
    os.chdir(each_pert_output_run)
    cmds = [
        "cp " + each_pert_abs + "/" + solvation_complex + "/solvated.parm7 " + solvation_complex + "/input/SYSTEM.parm7",
        "cp " + each_pert_abs + "/" + solvation_complex + "/solvated.pdb " + solvation_complex + "/input/SYSTEM.pdb",
        "cp " + each_pert_abs + "/" + solvation_complex + "/solvated.rst7 " + solvation_complex + "/input/SYSTEM.rst7",
        "cp " + each_pert_abs + "/ligand.flex " + solvation_complex + "/input/MORPH.flex",
        "cp " + script_folder + "/sim_* " + solvation_complex + "/input/",
        "cp " + script_folder + "/cluster.sh " + solvation_complex + "/",
        "cp " + script_folder + "/serial_" + calculation_format  + ".sh "+solvation_complex+"/serial.sh",
        "cp " + each_pert_abs + "/MORPH." + calculation_format + ".pert " + solvation_complex + "/input/MORPH.pert"]
    for cmd in cmds:
        print(cmd)
        os.system(cmd)


def check_pert_state(each_pert_abs):
    states = {'decharge': False,
              'recharge': False,
              'vdw': False,
              'onestep': False,
              'charge': False}

    decharge_file = each_pert_abs + "/MORPH.decharge.pert"
    recharge_file = each_pert_abs + "/MORPH.recharge.pert"
    charge_file = each_pert_abs + "/MORPH.charge.pert"
    onestep_file = each_pert_abs + "MORPH.onestep.pert"
    vdw_file = each_pert_abs + "/MORPH.vdw.pert"
    try:
        os.stat(decharge_file)
        states["decharge"] = True
        # print(each_pert_abs, "has decharge")
    except:
        print(each_pert_abs, "has no decharge")
    try:
        os.stat(recharge_file)
        states["recharge"] = True
        # print(each_pert_abs, "has recharge")
    except:
        print(each_pert_abs, "has no recharge")
    try:
        os.stat(charge_file)
        states["charge"] = True
        # print(each_pert_abs, "has charge")
    except:
        print(each_pert_abs, "has no charge")
    try:
        os.stat(vdw_file)
        states["vdw"] = True
        # print(each_pert_abs, "has vdw")
    except:
        print(each_pert_abs, "has no vdw")

    try:
        os.stat(onestep_file)
        states["onestep"] = True
        # print(each_pert_abs, "has vdw")
    except:
        print(each_pert_abs, "has one step")
    return states


def make_run_folder(each_pert_out, run_type):
    each_pert_output_run = each_pert_out + "/"+run_type
    each_pert_out_run_free = each_pert_output_run + "/solvated"
    each_pert_out_run_bound = each_pert_output_run + "/complex"
    each_pert_out_run_free_input = each_pert_out_run_free + "/input"
    each_pert_out_run_free_output = each_pert_out_run_free + "/output"
    each_pert_out_run_bound_input = each_pert_out_run_bound + "/input"
    each_pert_out_run_bound_output = each_pert_out_run_bound + "/output"
    make_directory(each_pert_output_run)
    make_directory(each_pert_out_run_free)
    make_directory(each_pert_out_run_bound)
    make_directory(each_pert_out_run_free_input)
    make_directory(each_pert_out_run_free_output)
    make_directory(each_pert_out_run_bound_input)
    make_directory(each_pert_out_run_bound_output)
    return each_pert_output_run


if __name__ == "__main__":
    input_folder = os.path.abspath(args.input_folder)
    script_folder = os.path.abspath(args.script_folder)
    output_folder = os.path.abspath(args.output_folder)
    output_submit = output_folder+"/"+args.submit
    write_file(submit_lines, output_submit)
    make_directory(output_folder)
    all_pert_folder = os.listdir(input_folder)
    for each_pert in all_pert_folder:
        each_pert_abs = os.path.abspath(input_folder)+"/"+each_pert
        print ("the pert absolute path is:", each_pert_abs)
        charge_state = check_pert_state(each_pert_abs)
        each_pert_out = output_folder + "/" + each_pert
        make_directory(each_pert_out)

        """
        copy the input for run_no 0: the decharge process
        """
        for each_key in charge_state.keys():
            if charge_state[each_key]:
                each_pert_output_run = make_run_folder(each_pert_out, each_key)
                copy_file(each_pert_abs, solvation_complex="solvated", calculation_format=each_key,
                          script_folder=script_folder, each_pert_output_run=each_pert_output_run)
                os.chdir(output_folder)
                copy_file(each_pert_abs, solvation_complex="complex", calculation_format=each_key,
                          script_folder=script_folder, each_pert_output_run=each_pert_output_run)
                os.chdir(output_folder)
