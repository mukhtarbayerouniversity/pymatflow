"""
Overall representation of Abinit
"""

import os
import shutil

from pymatflow.abinit.base.input import abinit_input
from pymatflow.abinit.base.files import abinit_files



class abinit:
    """
    """
    def __init__(self):
        self.input = abinit_input()
        self.files = abinit_files()

        self.input.electrons.basic_setting()

        self._initialize()

    def _initialize(self):
        """ initialize the object, do some default setting
        """
        self.run_params  = {}
        self.set_run()

    def get_xyz(self, xyzfile):
        self.input.system.xyz.get_xyz(xyzfile)

    def set_params(self, params={}):
        self.input.set_params(params)

    def set_kpoints(self, kpoints={}):
        self.input.electrons.kpoints.set_params(kpoints)

    def set_properties(self, properties=[]):
        self.input.properties.get_option(option=properties)

    #

    def dft_plus_u(self):
        self.input.electrons.dft_plus_u()

    def set_run(self, mpi="", jobname="abinit", nodes=1, ppn=32):
        self.run_params["mpi"] = mpi
        self.run_params["jobname"] = jobname
        self.run_params["nodes"] = nodes
        self.run_params["ppn"] = ppn

    def run(self, directory="tmp-abinit-static", runopt="gen"):
        self.files.name = "abinit.files"
        self.files.main_in = "abinit.in"
        self.files.main_out = "abinit.out"
        self.files.wavefunc_in = "abinit-i"
        self.files.wavefunc_out = "abinit-o"
        self.files.tmp = "tmp"
        if runopt == "gen" or runopt == "genrun":
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.mkdir(directory)
            os.system("cp *.psp8 %s/" % directory)
            os.system("cp *.GGA_PBE-JTH.xml %s/" % directory)
            os.system("cp %s %s/" % (self.input.system.xyz.file, directory))

            self.input.electrons.set_scf_nscf("scf")


            # generate pbs job submit script
            self.gen_pbs(directory=directory, script="static-scf.pbs", cmd="abinit", jobname=jobname, nodes=nodes, ppn=ppn)

            # generate local bash job run script
            self.gen_bash(directory=directory, script="static-scf.sh", cmd="abinit", mpi=mpi)

        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            #os.system("abinit < %s" % inpname.split(".")[0]+".files")
            os.system("bash %s" % "static-scf.sh")
            os.chdir("../")

    def gen_yh(self, inpname, output, directory, cmd="abinit"):
        """
        generating yhbatch job script for calculation
        """
        with open(os.path.join(directory, inpname.split(".in")[0]+".sub"), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("yhrun -N 1 -n 24 %s < %s > %s\n" % (cmd, inpname, output))

    def gen_pbs(self, directory, script="abinit.pbs", cmd="abinit", jobname="abinit", nodes=1, ppn=32):
        """
        generating pbs job script for calculation
        """
        with open(os.path.join(directory, script),  'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % jobname)
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (nodes, ppn))
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("cat > %s<<EOF\n" % self.files.main_in)
            self.input.to_input(fout)
            fout.write("EOF\n")
            fout.write("cat > %s<<EOF\n" % self.files.name)
            self.files.to_files(fout, system=self.input.system)
            fout.write("EOF\n")
            fout.write("mpirun -np $NP -machinefile $PBS_NODEFILE %s < %s\n" % (cmd, self.files.name))

    def gen_bash(self, directory, script="abinit.sh", cmd="abinit", mpi=""):
        """
        generating pbs job script for calculation
        """
        with open(os.path.join(directory, script),  'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("cat > %s<<EOF\n" % self.files.main_in)
            self.input.to_input(fout)
            fout.write("EOF\n")
            fout.write("cat > %s<<EOF\n" % self.files.name)
            self.files.to_files(fout, system=self.input.system)
            fout.write("EOF\n")
            fout.write("%s %s < %s\n" % (mpi, cmd, self.files.name))
