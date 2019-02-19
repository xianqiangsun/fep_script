import os
import sys
import argparse

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-s', dest='script_folder', default="script", help="the input script file for the sire folder")
parser.add_argument('-o', dest='output_folder', default='sire')
parser.add_argument('-c', dest='convert', default=True)
args = parser.parse_args()


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
        if el[2:6]=="name":
            initial_LJ = all_lines[el_no+3].split()[1:]
            final_LJ = all_lines[el_no+4].split()[1:]
            atom_lj_dic[el.split()[1]]=[initial_LJ,final_LJ]
    return all_lj_dic


def decharge_file(input_file, output_file, vdw_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
    """
    all_lj_dic=vdw_name_LJ(vdw_file)
    a = open(input_file, 'r')
    out_f = open(output_file, "w")
    all_lines = []
    for l in a.readlines():
        all_lines.append(l)
    for el_no,el in enumerate(all_lines):
        if el[2:14] == "final_charge":
            all_lines[el_no]="     final_charge    0.00000\n"
            atom_name = all_lines[el_no-6].split()[-1]
            lj = all_lj_dic[atom_name]
            all_lines[el_no-2]="        initial_LJ      "+lj[0][0]+'  '+lj[0][1]
            all_lines[el_no-2]="        final_LJ        "+lj[0][0]+'  '+lj[0][1]
    for el in all_lines:
            out_f.write(el)


def recharge_file(input_file, output_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
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
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
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
            "cp %s/serial_vdw_free.sh free/serial.sh" % script_folder
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
            "cp %s/serial_vdw_bound.sh bound/serial.sh" % script_folder
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
            "cp %s/serial_recharge_free.sh free/serial.sh" % script_folder
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
            "cp %s/serial_recharge_bound.sh bound/serial.sh" % script_folder
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


def check_charge_state(each_pert_abs):
    decharge_file = each_pert_abs + "/MORPH.decharge.pert"
    try:
        os.stat(decharge_file)
        return True
    except:
        return False


def make_run_folder(each_pert_out, run_no):
    each_pert_output_run = each_pert_out + "/run%003d" % run_no
    each_pert_out_run_free = each_pert_out_run + "/free"
    each_pert_out_run_bound = each_pert_out_run + "/bound"
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


if __name__():
    input_folder = args.input_folder
    script_folder = args.script_folder
    output_folder = args.output_folder
    make_directory(output_folder)
    all_pert_folder = os.listdir(input_folder)
    for each_pert in all_pert_folder:
        each_pert_abs = os.path.abspath(each_pert)
        charge_state = check_charge_state(each_pert_abs)
        each_pert_out = output_folder + "/" + each_pert
        make_directory(each_pert_out)

        """
        copy the input for run_no 0: the decharge process
        """
        if charge_state and args.convert:
            run_no = 0
            each_pert_output_run = make_run_folder(each_pert_out, run_no)
            solvated_decharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            complex_decharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            """
            copy the input for run_no 1: the vdw process
            """
            run_no = 1
            each_pert_output_run = make_run_folder(each_pert_out, run_no)
            solvated_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            complex_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            """
            copy the input for run_no 2: the recharge process
            """
            run_no = 2
            each_pert_output_run = make_run_folder(each_pert_out, run_no)
            solvated_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            complex_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
        else:
            """
            copy the input for run_no 1: the vdw process
            need update in the future####################
            """
            run_no = 1
            each_pert_output_run = make_run_folder(each_pert_out, run_no)
            solvated_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            complex_vdw(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            """
            copy the input for run_no 2: the recharge process
            """
            run_no = 2
            each_pert_output_run = make_run_folder(each_pert_out, run_no)
            solvated_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
            complex_recharge(each_pert_abs, script_folder, charge_state, each_pert_output_run)
