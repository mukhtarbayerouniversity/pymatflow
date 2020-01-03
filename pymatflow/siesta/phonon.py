#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg

from pymatflow.siesta.base.system import siesta_system
from pymatflow.siesta.base.electrons import siesta_electrons
from pymatflow.siesta.base.ions import siesta_ions
from pymatflow.siesta.base.properties import siesta_properties

class phonon_run:
    """
    Note:
        we can use Util/vibra to extract phonon frequencies and vectors.
    """
    def __init__(self, xyz_f):
        self.system = siesta_system(xyz_f)
        self.electrons = siesta_electrons()
        self.ions = siesta_ions()
        # here self.properties is not used as in static calculation
        # we just utilize it to providing calculation of BornCharge
        # with self.properties.option = [6]
        self.properties = siesta_properties(self.system.xyz)
        
        self.electrons.basic_setting()
        self.ions.basic_setting(option="phonon")

    def phonon(self, directory="tmp-siesta-phonon", inpname="phonon.fdf", output="phonon.out",
            mpi="", runopt="gen", electrons={}, ions={}, kpoints_mp=[1, 1, 1], borncharge=False):
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
        
            for element in self.system.xyz.specie_labels:
                shutil.copyfile("%s.psf" % element, os.path.join(directory, "%s.psf" % element))
       
            self.electrons.kpoints_mp = kpoints_mp
            self.electrons.set_params(electrons)
            self.ions.set_params(ions)
            if borncharge == True:
                # here we use siesta_properties to provide calculation of Born  Effective Charge
                # along with force constants calculation.
                self.properties.options = [6] 
            #
            self.ions.params["Eigenvectors"] = "True" # to get the siesta.vectors file
            with open(os.path.join(directory, inpname), 'w') as fout:
                self.system.to_fdf(fout)
                self.electrons.to_fdf(fout)
                self.ions.to_fdf(fout)
                if borncharge == True:
                    self.properties.to_fdf(fout)

            # gen yhbatch script
            #self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="siesta")

        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("%s siesta < %s | tee %s" % (mpi, inpname, output))
            # analyse the result
            import matplotlib.pyplot as plt
            os.chdir("../")
