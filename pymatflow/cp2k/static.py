#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg
import matplotlib.pyplot as plt

from pymatflow.cp2k.base.glob import cp2k_glob
from pymatflow.cp2k.base.force_eval import cp2k_force_eval
#from emuhelper.cp2k.base.atom import cp2k_atom

"""
Usage:
"""

class static_run:
    """
    """
    def __init__(self, xyz_f):
        self.glob = cp2k_glob()
        self.force_eval = cp2k_force_eval(xyz_f)
 #       self.atom = cp2k_atom()
        
        self.glob.basic_setting(run_type="ENERGY_FORCE")
        self.force_eval.basic_setting()


    def scf(self, directory="tmp-cp2k-static", inpname="static-scf.inp", output="static-scf.out", 
            force_eval={}, mpi="", runopt="gen", printout_option=[]):
        """
        directory: a place for all the generated files
        """
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            shutil.copyfile(self.force_eval.subsys.xyz.file, os.path.join(directory, self.force_eval.subsys.xyz.file))
            # using force_eval
            self.force_eval.set_params(force_eval)
            #self.atom.set_params(atom)
            self.printout_option(printout_option)
            with open(os.path.join(directory, inpname), 'w') as fout:
                self.glob.to_input(fout)
                self.force_eval.to_input(fout)
                #self.atom.to_input(fout)
    
        if runopt == "run" or runopt == "genrun":
           os.chdir(directory)
           os.system("cp2k.psmp -in %s | tee %s" % (inpname, output))
           os.chdir("../")    

    def scf_restart(self, directory="tmp-cp2k-static", inpname="static-scf-restart.inp", output="static-scf-restart.out", 
            force_eval={}, mpi="", runopt="gen", printout_option=[]):
        """
        scf_restart continue a scf calculation from previous scf
        or mimic a nscf calculation(there seems no official nscf
        in cp2k) by increasing kpoints from previous scf running
        """
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("scf_restart calculation:\n")
            print("  directory of previous scf calculattion not found!\n")
            sys.exit(1)
        if runopt == "gen" or runopt == "genrun":
            self.force_eval.dft.scf.params["SCF_GUESS"] = "RESTART"
            # using force_eval
            self.force_eval.set_params(force_eval)
            self.printout_option(printout_option)
            with open(os.path.join(directory, inpname), 'w') as fout:
                self.glob.to_input(fout)
                self.force_eval.to_input(fout)
    
        if runopt == "run" or runopt == "genrun":
           os.chdir(directory)
           os.system("cp2k.psmp -in %s | tee %s" % (inpname, output))
           os.chdir("../")    
    
    def converge_cutoff(self, emin, emax, step, rel_cutoff, directory="tmp-cp2k-cutoff", 
            runopt="gen", force_eval={}):
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            shutil.copyfile(self.force_eval.subsys.xyz.file, os.path.join(directory, self.force_eval.subsys.xyz.file))
        
            n_test = int((emax - emin) / step)
            for i in range(n_test + 1):
                cutoff = int(emin + i * step)
                inpname = "cutoff-%d.inp" % cutoff
                self.force_eval.dft.mgrid.params["CUTOFF"] = cutoff
                self.force_eval.dft.mgrid.params["REL_CUTOFF"] = rel_cutoff
                self.force_eval.set_params(force_eval)
                with open(os.path.join(directory, inpname), 'w') as fout:
                    self.glob.to_input(fout)
                    self.force_eval.to_input(fout)
        # run
        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            for i in range(n_test + 1):
                cutoff = int(emin + i * step)
                inpname = "cutoff-%d.inp" % cutoff
                output = "cutoff-%d.out" % cutoff
                os.system("cp2k.psmp -in %s | tee %s" % (inpname, output))
            os.chdir("../")
            # analyse the result
            os.chdir(directory)
            for i in range(n_test + 1):
                cutoff = int(emin + i * step)
                out_f_name = "cutoff-%d.out" % cutoff
                os.system("cat %s | grep 'Total energy:' >> energy-cutoff.data" % out_f_name)
            cutoffs = [emin + i * step for i in range(n_test + 1)]
            energy = []
            with open("energy-cutoff.data", 'r') as fin:
                for line in fin:
                    energy.append(float(line.split()[2]))
            plt.plot(cutoffs, energy, marker='o')
            plt.title("CUTOFF Converge Test", fontweight='bold', color='red')
            plt.xlabel("CUTOFF (Ry)")
            plt.ylabel("Energy (a.u.)")
            plt.tight_layout()
            plt.grid(True)
            plt.savefig("energy-cutoff.png")
            plt.show()
            os.chdir("../")

    def converge_rel_cutoff(self, emin, emax, step, cutoff, directory="tmp-cp2k-rel-cutoff",
            force_eval={}, runopt="gen"):
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            shutil.copyfile(self.force_eval.subsys.xyz.file, os.path.join(directory, self.force_eval.subsys.xyz.file))
        
            n_test = int((emax - emin) / step)
            for i in range(n_test + 1):
                rel_cutoff = int(emin + i * step)
                inpname = "rel-cutoff-%d.inp" % rel_cutoff
                self.force_eval.dft.mgrid.params["CUTOFF"] = cutoff
                self.force_eval.dft.mgrid.params["REL_CUTOFF"] = rel_cutoff
                self.force_eval.set_params(force_eval)
                with open(os.path.join(directory, inpname), 'w') as fout:
                    self.glob.to_input(fout)
                    self.force_eval.to_input(fout)
        # run
        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            for i in range(n_test + 1):
                rel_cutoff = int(emin + i * step)
                inpname = "rel-cutoff-%d.inp" % rel_cutoff
                output = "rel-cutoff-%d.out" % rel_cutoff
                os.system("cp2k.psmp -in %s | tee %s" % (inpname, output))
            os.chdir("../")
            # analyse the result
            os.chdir(directory)
            for i in range(n_test + 1):
                rel_cutoff = int(emin + i * step)
                out_f_name = "rel-cutoff-%d.out" % rel_cutoff
                os.system("cat %s | grep 'Total energy:' >> energy-rel-cutoff.data" % out_f_name)
            rel_cutoffs = [emin + i * step for i in range(n_test + 1)]
            energy = []
            with open("energy-rel-cutoff.data", 'r') as fin:
                for line in fin:
                    energy.append(float(line.split()[2]))
            plt.plot(rel_cutoffs, energy, marker='o')
            plt.title("CUTOFF Converge Test", fontweight='bold', color='red')
            plt.xlabel("CUTOFF (Ry)")
            plt.ylabel("Energy (a.u.)")
            plt.tight_layout()
            plt.grid(True)
            plt.savefig("energy-cutoff.png")
            plt.show()
            os.chdir("../")

    def printout_option(self, option=[]):
        """
        option:
            0: do not printout properties
            1: printout pdos
            2: printout band
            3: printout electron densities
        """
        if 1 in option:
            self.force_eval.dft.printout.print_pdos()
        if 2 in option:
            self.force_eval.dft.printout.print_band(self.force_eval.subsys.xyz)
        if 3 in option:
            self.force_eval.dft.printout.print_electron_density()
        if 4 in option:
            self.force_eval.dft.printout.elf_cube = True
        if 5 in option:
            self.force_eval.dft.printout.mo = True
        if 6 in option:
            self.force_eval.dft.printout.mo_cubes = True
        if 7 in option:
            self.force_eval.dft.printout.mulliken = True
        if 8 in option:
            self.force_eval.dft.printout.stm = True
        if 9 in option:
            self.force_eval.dft.printout.tot_density_cube = True
        if 10 in option:
            self.force_eval.dft.printout.v_hartree_cube = True
        if 11 in option:
            self.force_eval.dft.printout.v_xc_cube = True
        if 12 in option:
            self.force_eval.dft.printout.xray_diffraction_spectrum = True
        if 13 in option:
            self.force_eval.properties.resp.status = True