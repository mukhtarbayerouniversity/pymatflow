#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg
import matplotlib.pyplot as plt

from pymatflow.siesta.base.system import siesta_system
from pymatflow.siesta.base.electrons import siesta_electrons
from pymatflow.siesta.base.ions import siesta_ions
from pymatflow.siesta.base.properties import siesta_properties

class siesta:
    """
    """
    def __init__(self):
        self.system = siesta_system()
        self.electrons = siesta_electrons()
        self.ions = siesta_ions()
        self.properties = siesta_properties()
        
        self.electrons.basic_setting()

    def get_xyz(self, xyzfile):
        self.system.xyz.get_xyz(xyzfile)
        self.properties.set_xyz(self.system.xyz) 

    def set_params(self, params={}):
        for item in params:
            if item in self.electrons.incharge:
                self.electrons.set_params({item: params[item]})
            elif item in self.ions.incharge:
                self.ions.set_params({item: params[item]})
            else:
                continue

    def set_kpoints(self, kpoints_mp=[1, 1, 1]):
        self.electrons.kpoints_mp = kpoints_mp
    
    def set_spin(self, spin="non-polarized"):
        self.electrons.set_spin(spin)

    def gen_yh(self, inpname, output, directory="tmp-siesta-static", cmd="siesta"):
        """
        generating yhbatch job script for calculation
        """
        with open(os.path.join(directory, inpname.split(".fdf")[0]+".sub"), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("yhrun -N 1 -n 24 %s < %s > %s\n" % (cmd, inpname, output))

    def gen_pbs(self, inpname, output, directory, cmd="siesta", jobname="siesta", nodes=1, ppn=32):
        """
        generating pbs job script for calculation
        """
        with open(os.path.join(directory, inpname.split(".fdf")[0]+".pbs"), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % jobname)
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (nodes, ppn))
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("mpirun -np $NP -machinefile $PBS_NODEFILE %s < %s > %s\n" % (cmd, inpname, output))

