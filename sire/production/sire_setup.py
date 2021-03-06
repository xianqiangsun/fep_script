import os
import sys
import numpy as np

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-s', dest='script_folder', default="script", help="the input script file for the sire folder")
parser.add_argument('-o', dest='output_folder', default='sire')
parser.add_argument('-d', dest='device', default="0,1", help="the available device number for the simulations")


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
    atom_dic = {}
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:6] == "name":
            initial_LJ = all_lines[el_no + 3].split()[1:]
            final_LJ = all_lines[el_no + 4].split()[1:]
            atom_name = el.split()[1]
            atom_start_type = all_lines[el_no + 1].split()[1]
            atom_end_type = all_lines[el_no + 2].split()[1]
            atom_start_charge = float(all_lines[el_no + 5].split()[1])
            atom_end_charge = float(all_lines[el_no + 6].split()[1])
            atom_dic[el.split()[1]] = [initial_LJ, final_LJ, atom_name, atom_start_type, atom_end_type,
                                       atom_start_charge, atom_end_charge]
    return atom_dic


def decharge_file(input_file, output_file, vdw_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
    """
    all_lj_dic = vdw_name_LJ(vdw_file)
    a = open(input_file, 'r')
    all_lines = []
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:14] == "final_charge":
            if all_lines[el_no - 6].split()[1][:2] != "DU":
                initial_charge = float(all_lines[el_no - 1].split()[1])
                original_final_charge = float(all_lines[el_no].split()[1])
                final_charge = round(np.average([initial_charge, original_final_charge]), 5)
                all_lines[el_no] = "\t\tfinal_charge{0:11.5f}\n".format(final_charge)
            elif all_lines[el_no - 6].split()[1][:2] == "DU":
                all_lines[el_no - 1] = "\t\tinitial_charge  0.00000\n"
                all_lines[el_no] = "\t\tfinal_charge    0.00000\n"
            atom_name = all_lines[el_no - 6].split()[-1]
            lj = all_lj_dic[atom_name][:2]
            atom_start_type = all_lj_dic[atom_name][3]
            all_lines[el_no - 3] = "\t\tinitial_LJ      " + lj[0][0] + '  ' + lj[0][1] + '\n'
            all_lines[el_no - 2] = "\t\tfinal_LJ        " + lj[0][0] + '  ' + lj[0][1] + '\n'
            all_lines[el_no - 4] = "\t\tfinal_type      " + atom_start_type + "\n"
            all_lines[el_no - 5] = "\t\tinitial_type    " + atom_start_type + "\n"
    write_list_file(all_lines,output_file)


def recharge_file(input_file, output_file, vdw_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
    """
    a = open(input_file, 'r')
    all_lines = []
    all_lj_dic = vdw_name_LJ(vdw_file)
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:16] == "initial_charge":
            if all_lines[el_no - 5].split()[1][:2] != "DU":
                final_charge = float(all_lines[el_no + 1].split()[1])
                original_initial_charge = float(all_lines[el_no].split()[1])
                initial_charge = round(np.average([original_initial_charge, final_charge]), 5)
                el = "\t\tinitial_charge{0:9.5f}\n".format(initial_charge)
            elif all_lines[el_no - 5].split()[1][:2] == "DU":
                all_lines[el_no] = "\t\tinitial_charge  0.00000\n"
            atom_name = all_lines[el_no - 5].split()[-1]
            atom_end_type = all_lj_dic[atom_name][4]
            all_lines[el_no - 3] = "\t\tfinal_type      " + atom_end_type + "\n"
            all_lines[el_no - 4] = "\t\tinitial_type    " + atom_end_type + "\n"
            all_lines[el_no] = el
    write_list_file(all_lines,output_file)


def combine_decharge_recharge(decharge_file,vdw_file, recharge_file):
    vdw = open(vdw_file, 'r')
    recharge = open(recharge_file, "r")
    decharge = open(decharge_file,'r')
    vdw_dic = vdw_name_LJ(vdw_file)
    decharge_dic = vdw_name_LJ(decharge_file)
    recharge_dic = vdw_name_LJ(recharge_file)
    print (decharge_dic)
    print (recharge_dic)
    vdw_list = []
    recharge_list = []
    decharge_list = []
    for el in vdw.readlines():
        vdw_list.append(el)
    for el in recharge.readlines():
        recharge_list.append(el)
    for el in decharge.readlines():
        decharge_list.append(el)
    middle_charge_dic = {}
    for el_no,el in enumerate(decharge_list):
        if el[2:6] == "name" and el.split()[1][:2] != "DU":
            atom_name = el.split()[1]
            print (atom_name)
            start_charge = decharge_dic[atom_name][6]
            final_charge = recharge_dic[atom_name][6]
            middle_charge= round(np.average([start_charge,final_charge]), 5)
            middle_charge_dic[atom_name]=middle_charge
            decharge_list[el_no+6] = "\t\tfinal_charge{0:11.5f}\n".format(middle_charge)
    for el_no,el in enumerate(recharge_list):
        if el[2:6] == "name" and el.split()[1][:2] != "DU":
            atom_name = el.split()[1]
            recharge_list[el_no+5] = "\t\tinitial_charge{0:9.5f}\n".format(middle_charge_dic[atom_name])
    for el_no,el in enumerate(recharge_list):
        if el[2:6] == "name" and el.split()[1][:2] != "DU":
            atom_name = el.split()[1]
            vdw_list[el_no+5] = "\t\tinitial_charge{0:9.5f}\n".format(middle_charge_dic[atom_name])
            vdw_list[el_no+6] = "\t\tfinal_charge{0:11.5f}\n".format(middle_charge_dic[atom_name])
    return decharge_list,vdw_list,recharge_list


def write_list_file(all_lines,output_file):
    output_f = open(output_file, 'w')
    for el in all_lines:
        output_f.write(el)
    output_f.close()


def pert_vdw_file(vdw_file, output_file, charge_file):
    """
    :param input_file: input file for the charge to generate decharge
    :return: the de charged file
    """
    a = open(vdw_file, 'r')
    all_lines = []
    charge_file_dic = vdw_name_LJ(charge_file)
    for l in a.readlines():
        all_lines.append(l)
    for el_no, el in enumerate(all_lines):
        if el[2:6] == "name":
            if el.split()[1][:2] != "DU":
                atom_name = el.split()[1]
                print (charge_file_dic[atom_name][-2:])
                charge = round(np.average(charge_file_dic[atom_name][-2:]), 5)
                all_lines[el_no + 5] = "\t\tinitial_charge{0:9.5f}\n".format(charge)
                all_lines[el_no + 6] = "\t\tfinal_charge{0:11.5f}\n".format(charge)
            elif el.split()[1][:2] == "DU":
                all_lines[el_no + 5] = "\t\tinitial_charge  0.00000\n"
                all_lines[el_no + 6] = "\t\tfinal_charge    0.00000\n"
    write_list_file(all_lines,output_file)


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
        #cmd = "cp %s/MORPH.decharge.pert free/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(decharge_list,"free/input/MORPH.pert")
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        decharge_file_output = "free/input/MORPH.pert"
        decharge_file(charge_file_input, decharge_file_output, vdw_file_input)
    os.chdir("../../../")


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
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(decharge_list,"bound/input/MORPH.pert")
        #cmd = "cp %s/MORPH.decharge.pert bound/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        decharge_file_output = "bound/input/MORPH.pert"
        decharge_file(charge_file_input, decharge_file_output, vdw_file_input)
    os.chdir("../../../")


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
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(vdw_list,"free/input/MORPH.pert")
        #cmd = "cp %s/MORPH.vdw.pert free/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
    else:
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        vdw_file_output = "free/input/MORPH.pert"
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        pert_vdw_file(vdw_file_input, vdw_file_output, charge_file_input)
    os.chdir("../../../")


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
        #cmd = "cp %s/MORPH.vdw.pert bound/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(vdw_list,"bound/input/MORPH.pert")
    else:
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        vdw_file_output = "bound/input/MORPH.pert"
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        pert_vdw_file(vdw_file_input, vdw_file_output, charge_file_input)
    os.chdir("../../../")


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
        #cmd = "cp %s/MORPH.recharge.pert free/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(recharge_list,"free/input/MORPH.pert")
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        recharge_file_output = "free/input/MORPH.pert"
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        recharge_file(charge_file_input, recharge_file_output,vdw_file_input)
    os.chdir("../../../")


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
        decharge_file_input = each_pert_abs+"/MORPH.decharge.pert"
        recharge_file_input = each_pert_abs+"/MORPH.recharge.pert"
        vdw_file_input = each_pert_abs+"/MORPH.vdw.pert"
        decharge_list,vdw_list,recharge_list=combine_decharge_recharge(decharge_file_input,vdw_file_input,recharge_file_input )
        write_list_file(recharge_list,"bound/input/MORPH.pert")
        #cmd = "cp %s/MORPH.recharge.pert bound/input/MORPH.pert" % each_pert_abs
        #os.system(cmd)
    else:
        charge_file_input = each_pert_abs + "/MORPH.charge.pert"
        recharge_file_output = "bound/input/MORPH.pert"
        vdw_file_input = each_pert_abs + "/MORPH.vdw.pert"
        recharge_file(charge_file_input, recharge_file_output,vdw_file_input)
    os.chdir("../../../")


def check_charge_state(each_pert_abs):
    decharge_file = each_pert_abs + "/MORPH.decharge.pert"
    try:
        os.stat(decharge_file)
        return True
    except:
        return False


def make_run_folder(each_pert_out, run_no):
    each_pert_out_run = each_pert_out + "/run%003d" % run_no
    each_pert_out_run_free = each_pert_out_run + "/free"
    each_pert_out_run_bound = each_pert_out_run + "/bound"
    each_pert_out_run_free_input = each_pert_out_run_free + "/input"
    each_pert_out_run_free_output = each_pert_out_run_free + "/output"
    each_pert_out_run_bound_input = each_pert_out_run_bound + "/input"
    each_pert_out_run_bound_output = each_pert_out_run_bound + "/output"
    make_directory(each_pert_out_run)
    make_directory(each_pert_out_run_free)
    make_directory(each_pert_out_run_bound)
    make_directory(each_pert_out_run_free_input)
    make_directory(each_pert_out_run_free_output)
    make_directory(each_pert_out_run_bound_input)
    make_directory(each_pert_out_run_bound_output)
    return each_pert_out_run


if __name__ == "__main__":
    input_folder = args.input_folder
    script_folder = os.path.abspath(args.script_folder)
    output_folder = args.output_folder
    device = args.device.split(',')
    make_directory(output_folder)
    all_pert_folder = os.listdir(input_folder)
    for each_pert in all_pert_folder:
        each_pert_abs = os.path.abspath(input_folder) + "/" + each_pert
        charge_state = check_charge_state(each_pert_abs)
        each_pert_out = output_folder + "/" + each_pert
        make_directory(each_pert_out)

        """
        copy the input for run_no 0: the decharge process
        """
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
