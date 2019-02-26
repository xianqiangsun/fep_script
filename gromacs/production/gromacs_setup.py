import os
import sys
import numpy as np

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-s', dest='script_folder', default="script", help="the input script file for the sire folder")
parser.add_argument('-o', dest='output_folder', default='gromacs')
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


def read_file(input_file):
    a = open(input_file, "r")
    all_lines = []
    for el in a.readlines():
        all_lines.append(el)
    a.close()
    return all_lines


def replace_line(all_lines, number, steps_number, time_step):
    for el_no, el in enumerate(all_lines):
        if el[:17] == "init_lambda_state":
            all_lines[el_no] = "init-lambda-state    =" + str(number) + '\n'
    for el_no, el in enumerate(all_lines):
        if el[:6] == "nsteps":
            all_lines[el_no] = "nsteps    =" + str(steps_number) + '\n'
    for el_no, el in enumerate(all_lines):
        if el[:6] == "dt":
            all_lines[el_no] = "nsteps    =" + str(time_step) + '\n'
    return all_lines


def write_file(all_lines, output_file):
    a = open(output_file, "w")
    for el in all_lines:
        a.writelines(el)
    a.close()


def check_pert_state(each_pert_abs):
    decharge_file = each_pert_abs + "/pert2.itp"
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

def check_lambda_length(mdp_list):
    for each_line in mdp_list:
        if each_line[:11]=="fep_lambdas":
            lambdas = each_line[11:].split()[1:]
            lambdas_nos = len(lambdas)
    return lambdas_nos

def change_lambda_state(mdp_list,lambda_no):
    for el_no,each_line in enumerate(mdp_list):
        if each_line[:17]=="init-lambda-state":
            mdp_list[el_no] = "init-lambda-state    ="+str(lambda_no)+'\n'
    return mdp_list


if __name__ == "__main__":
    input_folder = args.input_folder
    script_folder = os.path.abspath(args.script_folder)
    output_folder = args.output_folder
    device = args.device.split(',')
    make_directory(output_folder)
    all_pert_folder = os.listdir(input_folder)
    em_vdw = read_file(script_folder + '/em_vdw.mdp')
    em_charge = read_file(script_folder + '/em_charge.mdp')
    em_charge_vdw = read_file(script_folder + '/em_charge_vdw.mdp')
    em_vdw_charge = read_file(script_folder + '/em_vdw_charge.mdp')
    nvt_vdw = read_file(script_folder + '/nvt_vdw.mdp')
    nvt_charge = read_file(script_folder + '/nvt_charge.mdp')
    nvt_vdw_charge = read_file(script_folder + '/nvt_vdw_charge.mdp')
    nvt_charge_vdw = read_file(script_folder + '/nvt_charge_vdw.mdp')
    npt_vdw = read_file(script_folder + '/npt_vdw.mdp')
    npt_charge = read_file(script_folder + '/npt_charge.mdp')
    npt_vdw_charge = read_file(script_folder + '/npt_vdw_charge.mdp')
    npt_charge_vdw = read_file(script_folder + '/npt_charge_vdw.mdp')
    md_vdw = read_file(script_folder + '/md_vdw.mdp')
    md_charge = read_file(script_folder + '/md_charge.mdp')
    md_vdw_charge = read_file(script_folder + '/md_vdw_charge.mdp')
    md_charge_vdw = read_file(script_folder + '/md_charge_vdw.mdp')

    for each_pert in all_pert_folder:
        each_pert_abs = os.path.abspath(input_folder) + "/" + each_pert
        each_pert_out = output_folder + "/" + each_pert
        make_directory(each_pert_out)
        pert_state = check_pert_state(each_pert_abs)
        if pert_state:
            for run_no in range(2):
                each_pert_output_run = make_run_folder(each_pert_out, run_no)
                if run_no == 0:
                    lambda_nos = check_lambda_length(em_charge_vdw)
                    for lambda_no in range(lambda_nos):
                        em_charge_vdw_lambda = change_lambda_state(em_charge_vdw, lambda_no)
                        nvt_charge_vdw_lambda = change_lambda_state(nvt_charge_vdw, lambda_no)
                        npt_charge_vdw_lambda = change_lambda_state(npt_charge_vdw, lambda_no)
                        md_charge_vdw_lambda = change_lambda_state(md_charge_vdw, lambda_no)

                    cmds = ["cp "+each_pert_abs+''
                    ]
                    #decharge the system and vdw change md_charge_vdw.mdp

                elif run_no == 1:
                    #recharge of the system md_charge.mdp
                    pass

        else:
            for run_no in range(1):
                each_pert_output_run = make_run_folder(each_pert_out, run_no)
                if run_no == 0:
                    #decharge the system md_vdw_charge.mdp
                    pass
