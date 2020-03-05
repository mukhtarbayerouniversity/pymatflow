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
            self.gen_llhpc(directory=directory, inpname=inpname, output=output, cmd="siesta")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="siesta", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])
            # gen local bash script
            self.gen_bash(directory=directory, inpname=inpname, output=output, cmd="siesta", mpi=self.run_params["mpi"])

        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("%s $PMF_SIESTA < %s | tee %s" % (self.run_params["mpi"], inpname, output))
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
            self.ions.md["VariableCell"] = "true"
        else:
            print("==========================================\n")
            print("             WARNING !!!\n")
            print("opt mode can only be 0 or 1\n")
            print("where 0 is: MD.VariableCell = flase\n")
            print("and 1 is : MD.VariableCell = true\n")
            sys.exit(1)

    def cubic(self, directory="tmp-siesta-opt-cubic", runopt="gen", auto=0, na=10, stepa=0.05):
        """
        """
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        for element in self.system.xyz.specie_labels:
            shutil.copyfile("%s.psf" % element, os.path.join(directory, "%s.psf" % element))

        shutil.copyfile(self.system.xyz.file, os.path.join(directory, os.path.basename(self.system.xyz.file)))

        #
        os.chdir(directory)

        # gen llhpc script
        with open("opt-cubic.slurm", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#SBATCH -p %s\n" % self.run_params["partition"])
            fout.write("#SBATCH -N %d\n" % self.run_params["nodes"])
            fout.write("#SBATCH -n %d\n" % self.run_params["ntask"])
            fout.write("#SBATCH -J %s\n" % self.run_params["jobname"])
            fout.write("#SBATCH -o %s\n" % self.run_params["stdout"])
            fout.write("#SBATCH -e %s\n" % self.run_params["stderr"])
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
            fout.write("do\n")
            fout.write("  mkdir relax-${a}\n")
            fout.write("  cp *.psf relax-${a}/\n")
            fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
            fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
            fout.write("${a} 0.000000 0.000000\n")
            fout.write("0.000000 ${a} 0.000000\n")
            fout.write("0.000000 0.000000 ${a}\n")
            fout.write("EOF\n")
            fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
            fout.write("  cd relax-${a}/\n")
            fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
            fout.write("  cd ../\n")
            fout.write("done\n")


        # gen pbs script
        with open("opt-cubic.pbs", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % self.run_params["jobname"])
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (self.run_params["nodes"], self.run_params["ppn"]))
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
            fout.write("do\n")
            fout.write("  mkdir relax-${a}\n")
            fout.write("  cp *.psf relax-${a}/\n")
            fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
            fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
            fout.write("${a} 0.000000 0.000000\n")
            fout.write("0.000000 ${a} 0.000000\n")
            fout.write("0.000000 0.000000 ${a}\n")
            fout.write("EOF\n")
            fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
            fout.write("  cd relax-${a}/\n")
            fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
            fout.write("  cd ../\n")
            fout.write("done\n")


        # gen local bash script
        with open("opt-cubic.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")

            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
            fout.write("do\n")
            fout.write("  mkdir relax-${a}\n")
            fout.write("  cp *.psf relax-${a}/\n")
            fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
            fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
            fout.write("${a} 0.000000 0.000000\n")
            fout.write("0.000000 ${a} 0.000000\n")
            fout.write("0.000000 0.000000 ${a}\n")
            fout.write("EOF\n")
            fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
            fout.write("  cd relax-${a}/\n")
            fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
            fout.write("  cd ../\n")
            fout.write("done\n")


        # generate result analysis script
        os.system("mkdir -p post-processing")

        with open("post-processing/get_energy.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")
            # the comment
            fout.write("cat > energy-latconst.data <<EOF\n")
            fout.write("# format: a energy(eV)\n")
            fout.write("EOF\n")
            # end
            fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
            fout.write("do\n")
            fout.write("   energy=`cat ../relax-${a}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
            fout.write("  cat >> energy-latconst.data <<EOF\n")
            fout.write("${a} ${energy}\n")
            fout.write("EOF\n")
            fout.write("done\n")
            fout.write("cat > energy-latconst.gp<<EOF\n")
            fout.write("set term gif\n")
            fout.write("set output 'energy-latconst.gif'\n")
            fout.write("set title Energy Latconst\n")
            fout.write("set xlabel 'latconst(a)'\n")
            fout.write("set ylabel 'Energy'\n")
            fout.write("plot 'energy-latconst.data' w l\n")
            fout.write("EOF\n")

        #os.system("cd post-processing; bash get_energy.sh; cd ../")
        os.chdir("../")
        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("bash opt-cubic.sh")
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="opt-cubic", server=self.run_params["server"])


    def hexagonal(self, directory="tmp-siesta-hexagonal", runopt="gen", auto=0, na=10, nc=10, stepa=0.05, stepc=0.05):
        """
        """
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        for element in self.system.xyz.specie_labels:
            shutil.copyfile("%s.psf" % element, os.path.join(directory, "%s.psf" % element))

        shutil.copyfile(self.system.xyz.file, os.path.join(directory, os.path.basename(self.system.xyz.file)))

        #
        os.chdir(directory)
        # gen llhpc script
        with open("opt-hexagonal.llhpc", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#SBATCH -p %s\n" % self.run_params["partition"])
            fout.write("#SBATCH -N %d\n" % self.run_params["nodes"])
            fout.write("#SBATCH -n %d\n" % self.run_params["ntask"])
            fout.write("#SBATCH -J %s\n" % self.run_params["jobname"])
            fout.write("#SBATCH -o %s\n" % self.run_params["stdout"])
            fout.write("#SBATCH -e %s\n" % self.run_params["stderr"])
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    # here with the usage of length and scale in bs processing, we can make sure that number like '.123' will be correctly
                    # set as '0.123', namely the ommited 0 by bs by default is not ommited now!
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("${v21} ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.in > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass


        # gen pbs script
        with open("opt-hexagonal.pbs", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % self.run_params["jobname"])
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (self.run_params["nodes"], self.run_params["ppn"]))
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    # here with the usage of length and scale in bs processing, we can make sure that number like '.123' will be correctly
                    # set as '0.123', namely the ommited 0 by bs by default is not ommited now!
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("${v21} ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE PMF_SIESTA < optimization.in > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass

        # gen local bash script
        with open("opt-hexagonal.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")

            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    # here with the usage of length and scale in bs processing, we can make sure that number like '.123' will be correctly
                    # set as '0.123', namely the ommited 0 by bs by default is not ommited now!
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  vec21=`echo \"scale=6; result=${v21} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  vec22=`echo \"scale=6; result=${v22} * ${a} / ${v11}; if (length(result)==scale(result)) print 0; print result\" | bc`\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("${vec21} ${vec22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("${v21} ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass


        # generate result analysis script
        os.system("mkdir -p post-processing")

        with open("post-processing/get_energy.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")
            # the comment
            if na >= 2 and nc >= 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: a c energy(eV)\n")
                fout.write("EOF\n")
            if na >= 2 and nc < 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: a energy(eV)\n")
                fout.write("EOF\n")
            if na < 2 and nc >= 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: c energy(eV)\n")
                fout.write("EOF\n")
            # end
            if na >= 2:
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("   energy=`cat ../relax-${a}-${c}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${a} ${c} ${energy}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")
                    fout.write("done\n")

                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(a)'\n")
                    fout.write("set ylabel 'latconst(c)'\n")
                    fout.write("set zlabel 'Energy'\n")
                    fout.write("splot 'energy-latconst.data'\n")
                    fout.write("EOF\n")
                else:
                    fout.write("   energy=`cat ../relax-${a}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${a} ${energy}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")

                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(a)'\n")
                    fout.write("set ylabel 'Energy'\n")
                    fout.write("plot 'energy-latconst.data' w l\n")
                    fout.write("EOF\n")
            else:
                if nc >= 2:
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("   energy=`cat ../relax-${c}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${c} ${energy}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")
                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(c)'\n")
                    fout.write("set ylabel 'Energy'\n")
                    fout.write("plot 'energy-latconst.data' w l\n")
                    fout.write("EOF\n")
                else:
                    # nothing to do
                    pass
        #os.system("cd post-processing; bash get_energy.sh; cd ../")
        os.chdir("../")
        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("bash opt-hexagonal.sh")
            os.chdir("../")

        server_handle(auto=auto, directory=directory, jobfilebase="opt-hexagonal", server=self.run_params["server"])

    def tetragonal(self, directory="tmp-siesta-opt-tetragonal", runopt="gen", auto=0, na=10, nc=10, stepa=0.05, stepc=0.05):
        """
        """
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        for element in self.system.xyz.specie_labels:
            shutil.copyfile("%s.psf" % element, os.path.join(directory, "%s.psf" % element))

        shutil.copyfile(self.system.xyz.file, os.path.join(directory, os.path.basename(self.system.xyz.file)))

        #
        os.chdir(directory)
        # gen llhpc script
        with open("opt-tetragonal.slurm", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#SBATCH -p %s\n" % self.run_params["partition"])
            fout.write("#SBATCH -N %d\n" % self.run_params["nodes"])
            fout.write("#SBATCH -n %d\n" % self.run_params["ntask"])
            fout.write("#SBATCH -J %s\n" % self.run_params["jobname"])
            fout.write("#SBATCH -o %s\n" % self.run_params["stdout"])
            fout.write("#SBATCH -e %s\n" % self.run_params["stderr"])
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp  *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp  *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("0.000000 ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  yhrun $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass

        # gen pbs script
        with open("opt-tetragonal.pbs", 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % self.run_params["jobname"])
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (self.run_params["nodes"], self.run_params["ppn"]))
            fout.write("\n")
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp  *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp  *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("0.000000 ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  mpirun -np $NP -machinefile $PBS_NODEFILE $PMF_SIESTA < optimization.fdf > optimization.out\n")
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass

        # gen local bash script
        with open("opt-tetragonal.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")

            fout.write("cat > optimization.fdf<<EOF\n")
            self.system.to_fdf(fout)
            self.electrons.to_fdf(fout)
            self.ions.to_fdf(fout)
            fout.write("EOF\n")

            a = self.system.xyz.cell[0][0]

            fout.write("v11=%f\n" % self.system.xyz.cell[0][0])
            fout.write("v12=%f\n" % self.system.xyz.cell[0][1])
            fout.write("v13=%f\n" % self.system.xyz.cell[0][2])
            fout.write("v21=%f\n" % self.system.xyz.cell[1][0])
            fout.write("v22=%f\n" % self.system.xyz.cell[1][1])
            fout.write("v23=%f\n" % self.system.xyz.cell[1][2])
            fout.write("v31=%f\n" % self.system.xyz.cell[2][0])
            fout.write("v32=%f\n" % self.system.xyz.cell[2][1])
            fout.write("v33=%f\n" % self.system.xyz.cell[2][2])

            fout.write("lat_vec_begin=`cat optimization.fdf | grep -n \'%block LatticeVectors\' | cut -d \":\" -f 1`\n")
            fout.write("lat_vec_end=`cat optimization.fdf | grep -n \'%endblock LatticeVectors\' | cut -d \":\" -f 1`\n")

            if na >= 2:
                # a is optimized
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    # optimize both a and c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${a}-${c}\n")
                    fout.write("  cp  *.psf relax-${a}-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}-${c}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${a}-${c}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # only optimize a
                    fout.write("  mkdir relax-${a}\n")
                    fout.write("  cp  *.psf relax-${a}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${a}/optimization.fdf\n")
                    fout.write("  cat >> relax-${a}/optimization.fdf<<EOF\n")
                    fout.write("${a} 0.000000 0.000000\n")
                    fout.write("0.000000 ${a} 0.000000\n")
                    fout.write("0.000000 0.000000 ${v33}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${a}/optimization.fdf\n")
                    fout.write("  cd relax-${a}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                fout.write("done\n")
            else:
                # a is not optimized
                if nc >= 2:
                    # only optimize c
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("  mkdir relax-${c}\n")
                    fout.write("  cp  *.psf relax-${c}/\n")
                    fout.write("  cat optimization.fdf | head -n +${lat_vec_begin} > relax-${c}/optimization.fdf\n")
                    fout.write("  cat >> relax-${c}/optimization.fdf<<EOF\n")
                    fout.write("${v11} 0.000000 0.000000\n")
                    fout.write("0.000000 ${v22} 0.000000\n")
                    fout.write("0.000000 0.000000 ${c}\n")
                    fout.write("EOF\n")
                    fout.write("  cat optimization.fdf | tail -n +${lat_vec_end} >> relax-${c}/optimization.fdf\n")
                    fout.write("  cd relax-${c}/\n")
                    fout.write("  %s $PMF_SIESTA < optimization.fdf | tee optimization.out\n" % self.run_params["mpi"])
                    fout.write("  cd ../\n")
                    fout.write("done\n")
                else:
                    # neither a or c is optimized
                    pass


        # generate result analysis script
        os.system("mkdir -p post-processing")

        with open("post-processing/get_energy.sh", 'w') as fout:
            fout.write("#!/bin/bash\n")
            # the comment
            if na >= 2 and nc >= 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: a c energy(eV)\n")
                fout.write("EOF\n")
            if na >= 2 and nc < 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: a energy(eV)\n")
                fout.write("EOF\n")
            if na < 2 and nc >= 2:
                fout.write("cat > energy-latconst.data <<EOF\n")
                fout.write("# format: c energy(eV)\n")
                fout.write("EOF\n")
            # end
            if na >= 2:
                fout.write("for a in `seq -w %f %f %f`\n" % (a-na/2*stepa, stepa, a+na/2*stepa))
                fout.write("do\n")
                if nc >= 2:
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("   energy=`cat ../relax-${a}-${c}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${a} ${c} ${energy:32:-36}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")
                    fout.write("done\n")

                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(a)'\n")
                    fout.write("set ylabel 'latconst(c)'\n")
                    fout.write("set zlabel 'Energy'\n")
                    fout.write("splot 'energy-latconst.data'\n")
                    fout.write("EOF\n")
                else:
                    fout.write("   energy=`cat ../relax-${a}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${a} ${energy:32:-36}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")

                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(a)'\n")
                    fout.write("set ylabel 'Energy'\n")
                    fout.write("plot 'energy-latconst.data' w l\n")
                    fout.write("EOF\n")
            else:
                if nc >= 2:
                    fout.write("for c in `seq -w %f %f %f`\n" % (c-nc/2*stepc, stepc, c+nc/2*stepc))
                    fout.write("do\n")
                    fout.write("   energy=`cat ../relax-${c}/optimization.out | grep 'Total =' | tail -n -1 | cut -d \"=\" -f 2`\n")
                    fout.write("  cat >> energy-latconst.data <<EOF\n")
                    fout.write("${c} ${energy:32:-36}\n")
                    fout.write("EOF\n")
                    fout.write("done\n")
                    fout.write("cat > energy-latconst.gp<<EOF\n")
                    fout.write("set term gif\n")
                    fout.write("set output 'energy-latconst.gif'\n")
                    fout.write("set title Energy Latconst\n")
                    fout.write("set xlabel 'latconst(c)'\n")
                    fout.write("set ylabel 'Energy'\n")
                    fout.write("plot 'energy-latconst.data' w l\n")
                    fout.write("EOF\n")
                else:
                    # nothing to do
                    pass
        #os.system("cd post-processing; bash get_energy.sh; cd ../")
        os.chdir("../")
        if runopt == "run" or runopt == "genrun":
            # run the simulation
            os.chdir(directory)
            os.system("bash opt-tetragonal.sh")
            os.chdir("../")

        server_handle(auto=auto, directory=directory, jobfilebase="opt-tetragonal", server=self.run_params["server"])
