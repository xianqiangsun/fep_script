import pytest
import pandas as pd
from alchemlyb.parsing import amber
from alchemlyb.estimators import MBAR
from alchemlyb.estimators import BAR
from alchemlyb.estimators import TI

import os
from os.path import isdir, join
from os import listdir
import copy
import numpy as np
"""
ti tutorial
https://github.com/alchemistry/alchemlyb/blob/master/docs/estimators-ti.rst
mbar tutorial

https://github.com/alchemistry/alchemlyb/blob/master/docs/estimators-fep.rst

python amber_half_analysis.py -i ../run -o energy.dat

"""

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-o', dest='output_file', default='output_energy.dat', help="the input file for the sire folder")

args = parser.parse_args()


def get_folders(input_folder):
    """
    :param input_folder:
    :return: the folder labels and its absolute path
    """
    folders = [f for f in listdir(input_folder) if isdir(join(input_folder, f))]
    folders_dic = {}
    for f in folders:
        folders_dic[f] = input_folder+"/"+str(f)
    return folders_dic

def get_calculation_type(folders_dic):
    type_dic = {}
    for ef in folders_dic.keys():
        ef_abs = folders_dic[ef]
        comp_solv_dic=get_folders(ef_abs)
        interaction_stage_dic={}
        for ef_comp_solv_dict in comp_solv_dic.keys():
            ef_comp_solv_dict_abs = comp_solv_dic[ef_comp_solv_dict]
            cal_type_dic=get_folders(ef_comp_solv_dict_abs)
            interaction_type_dic={}
            for ef_cal_type_dict in cal_type_dic.keys():
                lamda_value_list = []
                ef_cal_type_dict_abs = cal_type_dic[ef_cal_type_dict]
                lamda_dic = get_folders(ef_cal_type_dict_abs)
                for each_lamda in lamda_dic.values():
                    lamda_value_list.append(each_lamda+"/ti.out")
                interaction_type_dic[ef_cal_type_dict]=lamda_value_list
            interaction_stage_dic[ef_comp_solv_dict]=interaction_type_dic
        type_dic[ef]=interaction_stage_dic
    return type_dic



def get_calculation_values(type_dic):
    ti=copy.deepcopy(type_dic)
    #mbar=copy.deepcopy(type_dic)
    ti_function = TI()
    #mbar_function = MBAR()
    for ef_key in type_dic.keys():
        print (ef_key)
        ef_value = type_dic[ef_key]
        for ef_comp_sol_key in ef_value.keys():
            ef_comp_sol_value = ef_value[ef_comp_sol_key]
            for ef_cal_type_key in ef_comp_sol_value.keys():
                ef_cal_type_value = ef_comp_sol_value[ef_cal_type_key]
                ti_values = pd.concat([amber.extract_dHdl(ti) for ti in ef_cal_type_value])
                ti_function.fit(ti_values)
                ti[ef_key][ef_comp_sol_key][ef_cal_type_key] = ti_function.delta_f_.loc[0.00, 0.50]
                #print (ef_key,ef_comp_sol_key,ef_cal_type_key,ti_function.delta_f_, ti_function.d_delta_f_)
                #mbar_values = pd.concat([amber.extract_u_nk(ti) for ti in ef_cal_type_value])
                #print (mbar_values)
                #print (ti_values)
                #mbar_function.fit(mbar_values)
                #print (mbar_values)
                #print (mbar_function.delta_f_)
                #print (ef_key,ef_comp_sol_key,ef_cal_type_key,mbar_function.delta_f_.loc[0.00, 0.50])
                #mbar[ef_key][ef_comp_sol_value][ef_cal_type_key] = mbar_function.delta_f_.loc[0.00, 0.50]
    return ti

def energy_from_each_ti(each_ti_value):
    complex_energy = np.sum(list(each_ti_value["complex"].values()))
    solvation_energy = np.sum(list(each_ti_value["solvated"].values()))
    print (complex_energy, solvation_energy)
    return complex_energy,solvation_energy

def get_output_energy(ti):
    energy = {}
    for each_ti in ti.keys():
        value_split = each_ti.split("~")
        corr_ti = value_split[1]+"~"+value_split[0]
        each_ti_value = ti[each_ti]
        each_corr_ti_value = ti[corr_ti]
        #print (each_ti_value)
        complex_energy, solvation_energy = energy_from_each_ti(each_ti_value)
        corr_complex_energy, corr_solvation_energy=energy_from_each_ti(each_corr_ti_value)
        # the energy of transfering each compound from a to b, the more negative means the more favorable
        energy_diff =  complex_energy-solvation_energy - (corr_complex_energy - corr_solvation_energy)
        energy[each_ti]=energy_diff
        print (each_ti, energy_diff ,complex_energy-corr_complex_energy, solvation_energy - corr_solvation_energy)
    return energy


if __name__ == "__main__":

    all_folders = get_folders(args.input_folder)
    type_dic = get_calculation_type(all_folders)
    ti = get_calculation_values(type_dic)
    energy = get_output_energy(ti)
    energy_df=pd.Series(energy,index=energy.keys())
    energy_df.to_csv(args.output_file)

























