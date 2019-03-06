'''
analysis:
alchemical-analysis

test folder:
regor : /home/leos/work/hpk1/fep/fes_setup_amber
catipiller: /home/leos/hgst/working/regor/cdk/fep/fes_setup_1/test
test : python amber_setup.py -i ../_perturbations/pmemd -o .

kill nohup jobs

ps -aux | grep "sh subm"

export the CUDA device:

export CUDA_VISIBLE_DEVICES="0,1,2"

'''
import os
import sys
import numpy as np

import argparse

parser = argparse.ArgumentParser(description="Main script for setup the simulations of sire")

parser.add_argument('-i', dest='input_folder', default='_perturb', help="the input file for the sire folder")
parser.add_argument('-s', dest='script_folder', default="script", help="the input script file for the sire folder")
parser.add_argument('-o', dest='output_folder', default='amber')
parser.add_argument('-d', dest='device', default="0, 1", help="the available device number for the simulations")
parser.add_argument('-charge_lambda', dest='charge_lambda', default="0.0, 0.2, 0.4, 0.6, 0.8, 1.0",
                    help="the lambda values for the charge")
parser.add_argument('-vdw_lambda', dest='vdw_lambda', default="0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0",
                    help="the lambda values for the vdw")

args = parser.parse_args()

min_in = '''minimisation
 &cntrl
   imin = 1, ntmin = 2,
   maxcyc = 1000,
   ntpr = 20, ntwe = 20,
   ntb = 1,
   ntr = 1, restraint_wt = 5.00,
   restraintmask='!:WAT & !@H=',
'''

'''
   icfe = 1, ifsc = 1, clambda = 0.5, scalpha = 0.5, scbeta = 12.0,
   logdvdl = 0,
   timask1 = ':BNZ', timask2 = ':PHN',
   scmask1 = ':BNZ@H6', scmask2 = ':PHN@O1,H6'
 /
 &ewald
 /
 '''
heat_in_start = '''heating
 &cntrl
   imin = 0, nstlim = 20000, irest = 0, ntx = 1, dt = 0.002,
   nmropt = 1,
   ntt = 1, temp0 = 298.0, tempi = 5.0, tautp = 1.0,
   ntb = 1,
   ntc = 2, ntf = 1,
   ioutfm = 1, iwrap = 1,
   ntwe = 1000, ntwx = 1000, ntpr = 1000, ntwr = 5000,

   ntr = 1, restraint_wt = 5.00,
   restraintmask='!:WAT & !@H=',
'''

heat_in_end = ''' /
 &ewald
 /

 &wt
   type='TEMP0',
   istep1 = 0, istep2 = 10000,
   value1 = 5.0, value2 = 298.0
 /

 &wt type = 'END'
 /
'''

press_in = '''pressurising
 &cntrl
   imin = 0, nstlim = 20000, irest = 1, ntx = 5, dt = 0.002,
   ntt = 1, temp0 = 298.0, tautp = 5.0,
   ntp = 1, pres0 = 1.0, taup = 5.0,
   ntb = 2,
   ntc = 2, ntf = 1,
   ioutfm = 1, iwrap = 1,
   ntwe = 1000, ntwx = 1000, ntpr = 1000, ntwr = 5000,

   ntr = 1, restraint_wt = 5.00,
   restraintmask='!:WAT & !@H=',
'''

ti_in = '''TI/FEP, NpT, recharge transformation                                 
 &cntrl                                                              
 ! please adjust namelist parameters to your needs!                  
                                                                     
 ! parameters for general MD                                         
  imin = 0, nstlim = 500000, irest = 1, ntx = 5, dt = 0.002,    
  ntt = 3, temp0 = 298.0, gamma_ln = 2.0, ig = -1,                    
  ntb = 2,                                                            
  ntp = 1, barostat = 1, pres0 = 1.01325, taup = 2.0,                 
  ntwe = 10000, ntwx = 10000, ntpr = 500, ntwr = 50000, ntave = 50000,
  ioutfm = 1, iwrap = 1, ntxo = 2,                                    
                                                                     
  ! parameters for alchemical free energy simulation                  
  ntc = 2, ntf = 1,                                                   
  noshakemask = ':1,2',
  
'''
end_text = ''' /
 &ewald
 /
'''

sub_sh_start = '''#!/bin/sh
#
# Run all ligand simulations.  This is mostly a template for the LSF job
# scheduler.
#
mdrun=$AMBERHOME/bin/pmemd.MPI
pmemd_cuda=$AMBERHOME/bin/pmemd.cuda
pmemd_mpi="mpirun -np 20 $AMBERHOME/bin/pmemd.MPI"
pmemd=$AMBERHOME/bin/pmemd

'''

sub_sh_end = '''
#for w in $windows; do
echo "Min"
$pmemd \
  -i min.in -p ${file_name}.parm7 -c ${file_name}.rst7 \
  -ref ${file_name}.rst7 \
  -O -o min.out -e min.en -inf min.info -r min.rst7 -l min.log

echo "Heating..."
$pmemd_cuda \
  -i heat.in -p ${file_name}.parm7 -c min.rst7 -ref ${file_name}.rst7 \
  -O -o heat.out -e heat.en -inf heat.info -r heat.rst7 -x heat.nc -l heat.log

echo "Pressurising..."
$pmemd_mpi \
  -i press.in -p ${file_name}.parm7 -c heat.rst7 -ref heat.rst7 \
  -O -o press.out -e press.en -inf press.info -r press.rst7 -x press.nc \
  -l press.log

echo "TI..."
$pmemd_cuda \
  -i ti.in -p ${file_name}.parm7 -c press.rst7 -ref press.rst7 \
  -O -o ti.out -e ti.en -inf ti.info -r ti.rst7 -x ti.nc \
  -l ti.log
cd ../
done

'''

collection_sub_sh = '''#!/bin/sh\n'''


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


def write_file(all_lines, output_file):
    a = open(output_file, "w")
    for el in all_lines:
        a.writelines(el)
    a.close()


def check_pert_state(each_pert_abs):
    states = {'decharge': False,
              'recharge': False,
              'charge': False}

    decharge_file = each_pert_abs + "/decharge.in"
    recharge_file = each_pert_abs + "/recharge.in"
    charge_file = each_pert_abs + "/charge.in"
    try:
        os.stat(decharge_file)
        states["decharge"] = True
        print(each_pert_abs, "has decharge")
    except:
        print(each_pert_abs, "has no decharge")
    try:
        os.stat(recharge_file)
        states["recharge"] = True
        print(each_pert_abs, "has recharge")
    except:
        print(each_pert_abs, "has no recharge")
    try:
        os.stat(charge_file)
        states["charge"] = True
        print(each_pert_abs, "has charge")
    except:
        print(each_pert_abs, "has no charge")
    return states


def obtain_ifce_line(original_input, lambda_no):
    ifce_line = '''
    '''
    for el in original_input:
        if el[:5] == " icfe":
            ifce_line = el.replace("clambda = %L%", "clambda = " + str(lambda_no))
            print("the ifce line at: ", lambda_no, " is")
            print(ifce_line)
    return ifce_line


def obtain_mask_line(original_input):
    mask_line = ''''''
    for el in original_input:
        if el[:8] == " timask1":
            mask_line = mask_line + " " + el
        elif el[:7] == "scmask1":
            mask_line = mask_line + "  " + el
        elif el[:7] == "scmask2":
            mask_line = mask_line + "  " + el
        elif el[:8] == " crgmask":
            mask_line = mask_line + " " + el
    print("the mask line is:")
    print(mask_line)
    return mask_line


def obtain_ifmbar(lambdas, lambda_list):
    state_number = len(lambda_list)
    mbar_line = "  ifmbar = 1, bar_intervall = 500, mbar_states = " + str(state_number) + "\n"
    mbar_lambda = "  mbar_lambda = " + lambdas + '\n'
    mbar = mbar_line + mbar_lambda
    print("the mbar line is:")
    print(mbar)
    return mbar


def prepare_folder_and_configuration(each_pert_out, each_pert_abs, folder_name, lambda_values):
    # make the vdw input folder
    each_pert_out_run_complex = each_pert_out + "/complex"
    each_pert_out_run_solvated = each_pert_out + "/solvated"
    each_pert_out_run_complex_vdw = each_pert_out_run_complex + "/" + folder_name
    each_pert_out_run_solvated_vdw = each_pert_out_run_solvated + "/" + folder_name
    make_directory(each_pert_out_run_complex_vdw)
    make_directory(each_pert_out_run_solvated_vdw)

    # read the vdw simulation data
    original_vdw_in = read_file(each_pert_abs + '/complex/' + folder_name + '.in')  # complex and solvated are the same
    mask_line = obtain_mask_line(original_vdw_in)
    lambda_list = lambda_values.split(",")

    vdw_mbar = obtain_ifmbar(lambda_values, lambda_list)

    for each_lambda in lambda_list:
        each_lambda = each_lambda.strip()
        output_folder_complex = each_pert_out_run_complex_vdw + "/" + str(each_lambda)
        output_folder_solvated = each_pert_out_run_solvated_vdw + "/" + str(each_lambda)
        make_directory(output_folder_complex)
        make_directory(output_folder_solvated)

        each_pert_out_run_complex_vdw_min_in = each_pert_out_run_complex + "/" + folder_name + "/" + str(
            each_lambda) + "/min.in"
        each_pert_out_run_solvated_vdw_min_in = each_pert_out_run_solvated + "/" + folder_name + "/" + str(
            each_lambda) + "/min.in"
        each_pert_out_run_complex_vdw_heat_in = each_pert_out_run_complex + "/" + folder_name + "/" + str(
            each_lambda) + "/heat.in"
        each_pert_out_run_solvated_vdw_heat_in = each_pert_out_run_solvated + "/" + folder_name + "/" + str(
            each_lambda) + "/heat.in"
        each_pert_out_run_complex_vdw_press_in = each_pert_out_run_complex + "/" + folder_name + "/" + str(
            each_lambda) + "/press.in"
        each_pert_out_run_solvated_vdw_press_in = each_pert_out_run_solvated + "/" + folder_name + "/" + str(
            each_lambda) + "/press.in"
        each_pert_out_run_complex_vdw_ti_in = each_pert_out_run_complex + "/" + folder_name + "/" + str(
            each_lambda) + "/ti.in"
        each_pert_out_run_solvated_vdw_ti_in = each_pert_out_run_solvated + "/" + folder_name + "/" + str(
            each_lambda) + "/ti.in"

        ifce_line = obtain_ifce_line(original_vdw_in, each_lambda)
        min_in_vdw = min_in + ifce_line + vdw_mbar + mask_line + end_text
        min_in_vdw_solvated = open(each_pert_out_run_solvated_vdw_min_in, 'w')
        min_in_vdw_complex = open(each_pert_out_run_complex_vdw_min_in, 'w')
        min_in_vdw_solvated.writelines(min_in_vdw)
        min_in_vdw_solvated.close()
        min_in_vdw_complex.writelines(min_in_vdw)
        min_in_vdw_complex.close()

        heat_in_vdw = heat_in_start + ifce_line + vdw_mbar + mask_line + heat_in_end
        heat_in_vdw_solvated = open(each_pert_out_run_solvated_vdw_heat_in, 'w')
        heat_in_vdw_complex = open(each_pert_out_run_complex_vdw_heat_in, 'w')
        heat_in_vdw_solvated.writelines(heat_in_vdw)
        heat_in_vdw_solvated.close()
        heat_in_vdw_complex.writelines(heat_in_vdw)
        heat_in_vdw_complex.close()

        press_in_vdw = press_in + ifce_line + vdw_mbar + mask_line + end_text
        press_in_vdw_solvated = open(each_pert_out_run_solvated_vdw_press_in, 'w')
        press_in_vdw_complex = open(each_pert_out_run_complex_vdw_press_in, 'w')
        press_in_vdw_solvated.writelines(press_in_vdw)
        press_in_vdw_solvated.close()
        press_in_vdw_complex.writelines(press_in_vdw)
        press_in_vdw_complex.close()

        ti_in_vdw = ti_in + ifce_line + vdw_mbar + mask_line + end_text
        ti_in_vdw_solvated = open(each_pert_out_run_solvated_vdw_ti_in, 'w')
        ti_in_vdw_complex = open(each_pert_out_run_complex_vdw_ti_in, 'w')
        ti_in_vdw_solvated.writelines(ti_in_vdw)
        ti_in_vdw_solvated.close()
        ti_in_vdw_complex.writelines(ti_in_vdw)
        ti_in_vdw_complex.close()


def copy_system(each_pert_out, each_pert_abs, folder_name, lambda_values):
    lambda_list = lambda_values.split(",")
    each_pert_out_run_complex = each_pert_out + "/complex"
    each_pert_out_run_solvated = each_pert_out + "/solvated"
    each_pert_out_run_complex_vdw = each_pert_out_run_complex + "/" + folder_name
    each_pert_out_run_solvated_vdw = each_pert_out_run_solvated + "/" + folder_name
    original_file_complex = each_pert_abs + "/complex/"
    original_file_solvated = each_pert_abs + "/solvated/"
    for each_lambda in lambda_list:
        each_lambda = each_lambda.strip()
        cmds = ['cp ' + original_file_complex + folder_name + '.pdb ' + each_pert_out_run_complex_vdw + '/' + str(
            each_lambda),
                'cp ' + original_file_complex + folder_name + '.parm7 ' + each_pert_out_run_complex_vdw + '/' + str(
                    each_lambda),
                'cp ' + original_file_complex + folder_name + '.rst7 ' + each_pert_out_run_complex_vdw + '/' + str(
                    each_lambda),
                'cp ' + original_file_solvated + folder_name + '.pdb ' + each_pert_out_run_solvated_vdw + '/' + str(
                    each_lambda),
                'cp ' + original_file_solvated + folder_name + '.parm7 ' + each_pert_out_run_solvated_vdw + '/' + str(
                    each_lambda),
                'cp ' + original_file_solvated + folder_name + '.rst7 ' + each_pert_out_run_solvated_vdw + '/' + str(
                    each_lambda), ]
        for i in cmds:
            print(i)
            os.system(i)


def generate_sh_middle(folder_name, lambda_values):
    lambda_list = lambda_values.split(",")
    lambda_line = ""
    for el in lambda_list:
        lambda_line += el + " "
    print(lambda_line)
    mid_lines = ''''''
    mid_lines += "file_name=" + folder_name + "\n"
    mid_lines += "for i in " + lambda_line + ";\n"
    mid_lines += "do\n"
    mid_lines += "cd $i\n"
    return mid_lines


if __name__ == "__main__":
    input_folder = args.input_folder
    charge_lambda = args.charge_lambda
    vdw_lambda = args.vdw_lambda
    output_folder = args.output_folder
    charge_lambda_list = charge_lambda.split(",")
    vdw_lambda_list = vdw_lambda.split(",")
    all_pert_folder = os.listdir(input_folder)

    first_sub_line = "for i in "
    for each_pert in all_pert_folder:
        second_sub_line = "for j in $(ls -d */)"
        third_sub_line = "for k in $(ls -d */)"
        first_sub_line += each_pert + " "

        each_pert_abs = os.path.abspath(input_folder) + "/" + each_pert
        each_pert_out = output_folder + "/" + each_pert
        make_directory(each_pert_out)
        each_pert_out_run_complex = each_pert_out + "/complex"
        each_pert_out_run_solvated = each_pert_out + "/solvated"
        make_directory(each_pert_out_run_complex)
        make_directory(each_pert_out_run_solvated)
        states = check_pert_state(each_pert_abs)

        prepare_folder_and_configuration(each_pert_out, each_pert_abs, "vdw", vdw_lambda)
        copy_system(each_pert_out, each_pert_abs, "vdw", vdw_lambda)

        sh_mid_line = generate_sh_middle("vdw", vdw_lambda)
        sh_file = sub_sh_start + sh_mid_line + sub_sh_end

        write_file(sh_file, each_pert_out_run_complex + "/" + "vdw" + '/submit.sh')
        # make the recharge input
        if states["recharge"]:

            prepare_folder_and_configuration(each_pert_out, each_pert_abs, "recharge", charge_lambda)
            copy_system(each_pert_out, each_pert_abs, "recharge", charge_lambda)

            sh_mid_line = generate_sh_middle("recharge", charge_lambda)
            sh_file = sub_sh_start + sh_mid_line + sub_sh_end

            write_file(sh_file, each_pert_out_run_complex + "/" + "recharge" + '/submit.sh')
        # make the charge input
        if states["charge"]:
            prepare_folder_and_configuration(each_pert_out, each_pert_abs, "charge", charge_lambda)
            copy_system(each_pert_out, each_pert_abs, "charge", charge_lambda)

            sh_mid_line = generate_sh_middle("charge", charge_lambda)
            sh_file = sub_sh_start + sh_mid_line + sub_sh_end

            write_file(sh_file, each_pert_out_run_complex + "/" + "charge" + '/submit.sh')
        if states["decharge"]:
            prepare_folder_and_configuration(each_pert_out, each_pert_abs, "decharge", charge_lambda)
            copy_system(each_pert_out, each_pert_abs, "decharge", charge_lambda)

            sh_mid_line = generate_sh_middle("decharge", charge_lambda)
            sh_file = sub_sh_start + sh_mid_line + sub_sh_end

            write_file(sh_file, each_pert_out_run_complex + "/" + "decharge" + '/submit.sh')
    collection_sub_sh = collection_sub_sh + first_sub_line + ";\ndo\ncd $i\necho working on $i\n" + second_sub_line + ";\ndo\ncd $j\necho working on $j\n" + third_sub_line + ";\ndo\ncd $k\necho working on $k\n" + \
                        "sh submit.sh\n" + "\ncd ..\ndone\ncd ..\ndone\ncd ..\ndone"
    write_file(collection_sub_sh, output_folder + "/submit.sh")
