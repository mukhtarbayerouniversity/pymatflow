#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg

from pymatflow.cp2k.base.xyz import cp2k_xyz

from pymatflow.cp2k.base.glob import cp2k_glob
from pymatflow.cp2k.base.force_eval import cp2k_force_eval

"""
Usage:
    python phonon_cp2k.py xxx.xyz 
    xxx.xyz is the input structure file

    make sure the xyz structure file and pseudopotential file
    for all the elements of the system is in the directory.

Dependencies:
    pip install --user phonopy
    pip install --user cp2k_tools

Note:
    phonopy read the xxx.inp and it can only read the system structure
    by COORD specified in SUBSYS. So I can not use TOPOLOGY.
    PLUS: only scaled coordinates are currently supported!

References:
    https://www.cp2k.org/exercises:2018_uzh_cmest:phonon_calculation
"""


class phonopy_run:
    """
    """
    def __init__(self, xyz_f):
        self.glob = cp2k_glob()
        self.force_eval = cp2k_force_eval(xyz_f)
        
        self.glob.basic_setting(run_type="ENERGY_FORCE")
        self.force_eval.basic_setting()

        self.supercell_n = [1, 1, 1]


    def phonopy(self, directory="tmp-cp2k-phonopy",
            mpi="", runopt="gen", force_eval={}):
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            os.chdir(directory)
            shutil.copyfile("../%s" % self.force_eval.subsys.xyz.file, "%s" % self.force_eval.subsys.xyz.file)

            self.force_eval.set_params(force_eval)
            inp_name = "phonon.inp"
            with open(inp_name, 'w') as fout:
                self.glob.to_input(fout)
                #fout.write("\n")
                fout.write("&FORCE_EVAL\n")
                fout.write("\tMETHOD Quickstep\n")
            # subsys
            self.to_subsys_phonopy(inp_name)
            # end subsys
            with open(inp_name, 'a') as fout:
                # dft
                self.force_eval.dft.to_dft(fout)
                # end dft
                fout.write("&END FORCE_EVAL\n")


            # run the simulation
            os.system("phonopy --cp2k -c %s -d --dim='%d %d %d'" % (inp_name, self.supercell_n[0], self.supercell_n[1], self.supercell_n[2]))
            # now supercell-00x.inp is generated which will be used to construct input for cp2k
            os.system("ls | grep 'supercell-' > geo.data")
            disps = []
            with open("geo.data", 'r') as fin:
                for line in fin:
                    disps.append(line.split(".")[0].split("-")[1])

            for disp in disps:
                in_name = "supercell-%s.inp" % disp
                if os.path.exists(in_name) is not True:
                    break
                tmp_file = "supercell-%s.tmp.txt" % disp
                shutil.copyfile(in_name, tmp_file)
                # important: different disp calculation should have different PROJECT name
                self.glob.params["PROJECT"] = "abinitio" + "-supercell-" + disp
                with open(in_name, 'w') as fout:
                    self.glob.to_input(fout)
                    fout.write("\n")
                    fout.write("&FORCE_EVAL\n")
                    fout.write("\tMETHOD Quickstep\n")
                    fout.write("\t&SUBSYS\n")
                self.print_kinds(in_name)
                os.system("cat %s | sed '1d;2d;3d;4d;5d;6d;7d' | sed '$d' | sed '$d' | sed '$d' | sed '$d' | sed '$d' >> %s" % (tmp_file, in_name))
                with open(in_name, 'a') as fout:
                    fout.write("\t&END SUBSYS\n")
                    # dft
                    self.force_eval.dft.to_dft(fout)
                    # end dft
                    fout.write("\t&PRINT\n")
                    fout.write("\t\t&FORCES\n")
                    fout.write("\t\t\tFILENAME forces\n")
                    fout.write("\t\t&END FORCES\n")
                    fout.write("\t&END PRINT\n")
                    fout.write("&END FORCE_EVAL\n")

        if runopt == "run" or runopt == "genrun":
            for disp in disps:
                in_name = "supercell-%s.inp" % disp
                if os.path.exists(in_name) is not True:
                    break
                os.system("cp2k.psmp -in %s | tee %s" % (in_name, in_name+".out"))


            base_project_name = "ab-initio"
            phonopy_command = "phonopy --cp2k -f "
            for disp in disps:
                # important: different disp calculation should have different PROJECT name
                f_name = "abinitio" + "-supercell-" + disp + "-forces-1_0.xyz"
                if os.path.exists(f_name) is not True:
                    break
                phonopy_command = phonopy_command + f_name + " "
            os.system(phonopy_command)

            # get the band structure
            # 注意--pa设置Primitive Axis要设置正确! --band 控制了声子谱的图示
            os.system("phonopy --cp2k -c %s -p --dim='%d %d %d' --pa='1 0 0 0 1 0 0 0 1' --band='1/2 1/2 1/2 0 0 0 1/2 0 1/2'" % (inp_name, self.supercell_n[0], self.supercell_n[1], self.supercell_n[2]))

            # analyse the result

            import matplotlib.pyplot as plt

            #

    def to_subsys_phonopy(self, fname):
        cell = self.force_eval.subsys.xyz.cell
        with open(fname, 'a') as fout:
            fout.write("\t&SUBSYS\n")
            for element in self.force_eval.subsys.xyz.specie_labels:
                fout.write("\t\t&KIND %s\n" % element)
                fout.write("\t\t\tBASIS_SET DZVP-MOLOPT-SR-GTH\n")
                fout.write("\t\t\tPOTENTIAL GTH-PBE\n")
                fout.write("\t\t&END KIND\n")
            fout.write("\t\t&CELL\n")
            fout.write("\t\t\tABC %f %f %f\n" % (cell[0], cell[4], cell[8]))
            #fout.write("\t\t\tA %f %f %f\n" % (cell[0], cell[1], cell[2]))
            #fout.write("\t\t\tB %f %f %f\n" % (cell[3], cell[4], cell[5]))
            #fout.write("\t\t\tC %f %f %f\n" % (cell[6], cell[7], cell[8]))
            fout.write("\t\t&END CELL\n")
            #fout.write("\t\t&TOPOLOGY\n")
            #fout.write("\t\t\tCOORD_FILE_FORMAT xyz\n")
            #fout.write("\t\t\tCOORD_FILE_NAME %s\n" % sys.argv[1])
            #fout.write("\t\t&END TOPOLOGY\n")
            fout.write("\t\t&COORD\n")
            fout.write("\t\t\tSCALED .TRUE.\n")
            for atom in self.force_eval.subsys.xyz.atoms:
                fout.write("\t\t\t%s\t%f\t%f\t%f\n" % (atom.name, atom.x/cell[0], atom.y/cell[4], atom.z/cell[8]))
            fout.write("\t\t&END COORD\n")
            fout.write("\t&END SUBSYS\n")
            fout.write("\n")

    def print_kinds(self, fname):
        with open(fname, 'a') as fout:
            for element in self.force_eval.subsys.xyz.specie_labels:
                fout.write("\t\t&KIND %s\n" % element)
                fout.write("\t\t\tBASIS_SET DZVP-MOLOPT-SR-GTH\n")
                fout.write("\t\t\tPOTENTIAL GTH-PBE\n")
                fout.write("\t\t&END KIND\n")

