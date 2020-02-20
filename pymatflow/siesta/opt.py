"""
Geometric Optimization calc
"""
import numpy as np
import sys
import os
import shutil

from pymatflow.remote.server import server_handle

from pymatflow.siesta.siesta import siesta
#from pymatflow.siesta.base.system import siesta_system
#from pymatflow.siesta.base.electrons import siesta_electrons
#from pymatflow.siesta.base.ions import siesta_ions


class opt_run(siesta):
    """
    """
    def __init__(self):
        super().__init__()
        #self.system = siesta_system()
        #self.electrons = siesta_electrons()
        #self.ions = siesta_ions()

        self.electrons.basic_setting()
        self.ions.basic_setting(option="opt")


    def opt(self, directory="tmp-siesta-opt", inpname="geometric-optimization.fdf", output="geometric-optimization.out", runopt="gen", auto=0, mode=0):
        """
        :param mode:
            0: do not vary the cell
            1: vary the cell
        """
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)

            shutil.copyfile(self.system.xyz.file, os.path.join(directory, os.path.basename(self.system.xyz.file)))
            for element in self.system.xyz.specie_labels:
                shutil.copyfile("%s.psf" % element, os.path.join(directory, "%s.psf" % element))

            self.set_opt_mode(mode=mode)
            with open(os.path.join(directory, inpname), 'w') as fout:
                self.system.to_fdf(fout)
                self.electrons.to_fdf(fout)
                self.ions.to_fdf(fout)

            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="siesta")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="siesta", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])

        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("%s siesta < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="geometric-optimization", server=self.run_params["server"])

    def set_opt_mode(self, mode=0):
        """
        :param mode:
            0: do not variable cell
            1: variable cell
        """
        if mode == 0:
            self.ions.md["VariableCell"] = "false"
        elif mode == 1:
            self.ions.md["VariableCell"] = "false"
        else:
            print("==========================================\n")
            print("             WARNING !!!\n")
            print("opt mode can only be 0 or 1\n")
            print("where 0 is: MD.VariableCell = flase\n")
            print("and 1 is : MD.VariableCell = true\n")
            sys.exit(1)
