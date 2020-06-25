
import os
import sys
import shutil

from pymatflow.octopus.base.inp import inp
"""
"""

class octopus:
    """
    """
    def __init__(self):
        self.inp = inp()
        self._initialize()

    def _initialize(self):
        """ initialize the current object, do some default setting
        """
        self.run_params = {}
        self.set_run()

    def get_xyz(self, xyzfile):
        self.inp.system.xyz.get_xyz(xyzfile)

    def set_params(self, params, runtype=None):
        """
        :param runtype: one onf 'static', 'opt', 'phonopy', 'phonon', 'neb', 'md'
        """
        self.inp.set_params(params=params)

    def set_kpoints(self, kpoints_mp=[1, 1, 1, 0, 0, 0], option="mp",
            kpath=None):
        #self.kpoints.set_kpoints(kpoints_mp=kpoints_mp, option=option, kpath=kpath)
        self.inp.mesh.kpoints.params["KPointsGrid"] = kpoints_mp
        self.inp.mesh.kpoints.params["KPointsPath"] = kpath
        if option == "mp":
            self.inp.mesh.kpoints.params["KPointsPath"] = None
        else:
            self.inp.mesh.kpoints.params["KPointsGrid"] = None

    def set_run(self, mpi="", server="pbs", jobname="octopus", nodes=1, ppn=32, queue=None):
        """ used to set  the parameters controlling the running of the task
        :param mpi: you can specify the mpi command here, it only has effect on native running
        """
        self.run_params["server"] = server
        self.run_params["mpi"] = mpi
        self.run_params["jobname"] = jobname
        self.run_params["nodes"] = nodes
        self.run_params["ppn"] = ppn
        self.run_params["queue"] = queue

    def set_llhpc(self, partition="free", nodes=1, ntask=24, jobname="matflow_job", stdout="slurm.out", stderr="slurm.err"):
        self.run_params["partition"] = partition
        self.run_params["jobname"] = jobname
        self.run_params["nodes"] = nodes
        self.run_params["ntask"] = ntask
        self.run_params["stdout"] = stdout
        self.run_params["stderr"] = stderr

    def gen_llhpc(self, directory, scriptname="octopus.sub", cmd="$PMF_OCTOPUS"):
        """
        generating yhbatch job script for calculation
        """
        with open(os.path.join(directory, scriptname), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#SBATCH -p %s\n" % self.run_params["partition"])
            fout.write("#SBATCH -N %d\n" % self.run_params["nodes"])
            fout.write("#SBATCH -n %d\n" % self.run_params["ntask"])
            fout.write("#SBATCH -J %s\n" % self.run_params["jobname"])
            fout.write("#SBATCH -o %s\n" % self.run_params["stdout"])
            fout.write("#SBATCH -e %s\n" % self.run_params["stderr"])
            fout.write("cat > inp<<EOF\n")
            fout.write(self.inp.to_string())
            fout.write("EOF\n")
            fout.write("yhrun %s\n" % cmd)


    def gen_yh(self, directory, scriptname="octopus.sub", cmd="$PMF_OCTOPUS"):
        """
        generating yhbatch job script for calculation
        """
        with open(os.path.join(directory, scriptname), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("cat > INCAR<<EOF\n")
            fout.write(self.inp.to_string())
            fout.write("EOF\n")
            fout.write("yhrun -N 1 -n 24 %s\n" % (cmd))

    def gen_pbs(self, directory, cmd="$PMF_OCTOPUS", scriptname="ocotpus.pbs", jobname="vasp", nodes=1, ppn=32, queue=None):
        """
        generating pbs job script for calculation
        """
        with open(os.path.join(directory, scriptname), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % jobname)
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (nodes, ppn))
            if queue != None:
                fout.write("#PBS -q %s\n" % queue)            
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("cat > INCAR<<EOF\n")
            fout.write(self.inp.to_string())
            fout.write("EOF\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("mpirun -np $NP -machinefile $PBS_NODEFILE -genv I_MPI_FABRICS shm:tmi %s \n" % (cmd))

    def gen_bash(self, directory, mpi="", cmd="$PMF_OCTOPUS", scriptname="octopus.sh"):
        """
        generating bash script for local calculation
        """
        with open(os.path.join(directory, scriptname), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("\n")
            fout.write("cat > INCAR<<EOF\n")
            fout.write(self.inp.to_string())
            fout.write("EOF\n")
            fout.write("%s %s\n" % (mpi, cmd))

    def gen_lsf_sz(self, directory, cmd="$PMF_OCTOPUS", scriptname="octopus.lsf_sz", np=24, np_per_node=12):
        """
        generating lsf job script for calculation on ShenZhen supercomputer
        """
        with open(os.path.join(directory, scriptname), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("APP_NAME=intelY_mid\n")
            fout.write("NP=%d\n" % np)
            fout.write("NP_PER_NODE=%d\n" % np_per_node)
            fout.write("RUN=\"RAW\"\n")
            fout.write("CURDIR=$PWD\n")
            fout.write("#VASP=/home-yg/Soft/Vasp5.4/vasp_std\n")
            fout.write("source /home-yg/env/intel-12.1.sh\n")
            fout.write("source /home-yg/env/openmpi-1.6.5-intel.sh\n")
            fout.write("cd $CURDIR\n")
            fout.write("# starting creating ./nodelist\n")
            fout.write("rm -rf $CURDIR/nodelist >& /dev/null\n")
            fout.write("for i in `echo $LSB_HOSTS`\n")
            fout.write("do\n")
            fout.write("  echo \"$i\" >> $CURDIR/nodelist \n")
            fout.write("done\n")
            fout.write("ndoelist=$(cat $CURDIR/nodelist | uniq | awk \'{print $1}\' | tr \'\\n\' \',\')\n")

            fout.write("cat > INCAR<<EOF\n")
            fout.write(self.inp.to_string())
            fout.write("EOF\n")
            fout.write("mpirun -np $NP -machinefile $CURDIR/nodelist %s\n" % cmd)
