#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import shutil
import matplotlib.pyplot as plt

from emuhelper.abinit.base.electrons import abinit_electrons
from emuhelper.abinit.base.ions import abinit_ions
from emuhelper.abinit.base.system import abinit_system


class opt_run:
    """
    """
    def __init__(self, xyz_f):
        self.system = abinit_system(xyz_f)
        self.electrons = abinit_electrons()
        self.ions = abinit_ions()

        self.electrons.basic_setting()
        self.ions.basic_setting()

    def optimize(self, directory="tmp-abinit-opt", inpname="geometric-optimization.in", mpi="", runopt="gen",
            electrons={}, kpoints={}, ions={}):
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            os.system("cp *.psp8 %s/" % directory) 

            self.electrons.set_params(electrons)
            self.electrons.kpoints.set_kpoints(kpoints)
            self.ions.set_params(ions)
            with open(os.path.join(directory, inpname), 'w') as fout:
                self.electrons.to_in(fout)
                self.ions.to_in(fout)
                self.system.to_in(fout)

            with open(os.path.join(directory, inpname.split(".")[0]+".files"), 'w') as fout:
                fout.write("%s\n" % inpname)
                fout.write("%s.out\n" % inpname.split(".")[0])
                fout.write("%si\n" % inpname.split(".")[0])
                fout.write("%so\n" % inpname.split(".")[0])
                fout.write("temp\n")
                for element in self.system.xyz.specie_labels:
                    fout.write("%s\n" % (element + ".psp8"))

        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("abinit < %s" % inpname.split(".")[0]+".files")
            os.chdir("../")
    
    def analysis(self, directory="tmp-abinit-opt", inpname="geometric-optimization.in"):
        pass
