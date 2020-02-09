#!/usr/bin/env python
# _*_ coding: utf-8 _*_


import os
import shutil
import argparse


from pymatflow.cp2k.opt import opt_run
from pymatflow.base.server import server_handle

"""
Usage:
"""

params = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="directory of the calculation", type=str, default="tmp-cp2k-geo-opt-tetragonal")
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)

    parser.add_argument("--mpi", type=str, default="",
            help="MPI command: like 'mpirun -np 4'")

    parser.add_argument("--runopt", type=str, default="genrun", 
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    parser.add_argument("-p", "--printout-option", nargs="+", type=int,
            default=[],
            help="Properties printout option(0, 1, 2 implemented now), you can also activate multiple prinout-option at the same time")

    parser.add_argument("--ls-scf", type=str, default="FALSE",
            #choices=["TRUE", "FALSE", "true", "false"],
            help="use linear scaling scf method")
    
    parser.add_argument("--qs-method", type=str, default="GPW",
            choices=["AM1", "DFTB", "GAPW", "GAPW_XC", "GPW", "LRIGPW", "MNDO", "MNDOD", 
                "OFGPW", "PDG", "PM3", "PM6", "PM6-FM", "PNNL", "RIGPW", "RM1"],
            help="specify the electronic structure method")

    parser.add_argument("--eps-scf", type=float, default=1.0e-6,
            help="DFT-SCF-EPS_SCF")

    parser.add_argument("--xc-functional", type=str, default="PBE",
            help="XC_FUNCTIONAL type")

    parser.add_argument("--cutoff", type=int, default=100,
            help="CUTOFF, default value: 100 Ry, if you find your SCF hard to converge, you can try increasing CUTOFF")

    parser.add_argument("--rel-cutoff", type=int, default=60,
            help="REL_CUTOFF, default value: 60 Ry")

    parser.add_argument("-k", "--kpoints-scheme", type=str,
            default="GAMMA",
            help="DFT-KPOINTS-SCHEME(str): can be NONE, GAMMA, MONKHORST-PACK, MACDONALD, GENERAL. when you set MONKHORST-PACK, you should also add the three integers like 'monkhorst-pack 3 3 3'")
    
    parser.add_argument("--diag", type=str, default="TRUE",
            #choices=["TRUE", "FALSE", "true", "false"],
            help="whether choosing tranditional diagonalization for SCF")

    parser.add_argument("--ot", type=str, default="FALSE",
            #choices=["TRUE", "FALSE", "true", "false"],
            help="whether choosing orbital transformation for SCF")

    parser.add_argument("--alpha", type=float, default=0.4,
            help="DFT-SCF-MIXING-ALPHA")

    parser.add_argument("--smear", type=str, default="FALSE",
            #choices=["TRUE", "FALSE", "true", "false"],
            help="switch on or off smearing for occupation")

    parser.add_argument("--added-mos", help="ADDED_MOS for SCF", type=int, default=0)

    parser.add_argument("--smear-method", help="smearing type: FERMI_DIRAC, ENERGY_WINDOW", type=str, default="FERMI_DIRAC")

    parser.add_argument("--electronic-temp", help="ELECTRON_TEMPERATURE for FERMI_DIRAC SMEAR", type=float, default=300)

    parser.add_argument("--window-size", help="Size of the energy window centred at the Fermi level for ENERGY_WINDOW type smearing", type=float, default=0)

    # motion/geo_opt related
    parser.add_argument("--optimizer", type=str, default="BFGS",
            help="optimization algorithm for geometry optimization: BFGS, CG, LBFGS")
    parser.add_argument("--max-iter", type=int, default=200,
            help="maximum number of geometry optimization steps.")
    parser.add_argument("--type", type=str, default="MINIMIZATION",
            help="specify which kind of geometry optimization to perform: MINIMIZATION(default), TRANSITION_STATE")
    parser.add_argument("--max-dr", type=float, default=3e-3,
            help="Convergence criterion for the maximum geometry change between the current and the last optimizer iteration.")
    parser.add_argument("--max-force", type=float, default=4.50000000E-004,
            help="Convergence criterion for the maximum force component of the current configuration.")
    parser.add_argument("--rms-dr", type=float, default=1.50000000E-003,
            help="Convergence criterion for the root mean square (RMS) geometry change between the current and the last optimizer iteration.")
    parser.add_argument("--rms-force", type=float, default=3.00000000E-004,
            help="Convergence criterion for the root mean square (RMS) force of the current configuration.")
    # -----------------------------------------
    # na nc stepa stepc for hexagonal cell
    # -----------------------------------------
    parser.add_argument("--na", type=int, default=10,
            help="number of a used")
    parser.add_argument("--nc", type=int, default=10,
            help="number of c used")
    parser.add_argument("--stepa", type=float, default=0.05,
            help="a step")
    parser.add_argument("--stepc", type=float, default=0.05,
            help="c step")



    # -----------------------------------------------------------------
    #                      for server handling
    # -----------------------------------------------------------------
    parser.add_argument("--auto", type=int, default=0,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")
    parser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")
    parser.add_argument("--jobname", type=str, default="opt-tetragonal",
            help="jobname on the pbs server")
    parser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")
    parser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")



    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================   
    args = parser.parse_args()
    
    params["FORCE_EVAL-DFT-LS_SCF"] = args.ls_scf
    params["FORCE_EVAL-DFT-QS-METHOD"] = args.qs_method
    params["FORCE_EVAL-DFT-MGRID-CUTOFF"] = args.cutoff
    params["FORCE_EVAL-DFT-MGRID-REL_CUTOFF"] = args.rel_cutoff
    params["FORCE_EVAL-DFT-XC-XC_FUNCTIONAL"] = args.xc_functional
    params["FORCE_EVAL-DFT-SCF-EPS_SCF"] = args.eps_scf
    params["FORCE_EVAL-DFT-SCF-ADDED_MOS"] = args.added_mos
    params["FORCE_EVAL-DFT-SCF-SMEAR"] = args.smear
    params["FORCE_EVAL-DFT-SCF-SMEAR-METHOD"] = args.smear_method
    params["FORCE_EVAL-DFT-SCF-SMEAR-ELECTRONIC_TEMPERATURE"] = args.electronic_temp
    params["FORCE_EVAL-DFT-SCF-SMEAR-WINDOW_SIZE"] = args.window_size
    params["FORCE_EVAL-DFT-SCF-DIAGONALIZATION"] = args.diag
    params["FORCE_EVAL-DFT-SCF-OT"] = args.ot
    params["FORCE_EVAL-DFT-SCF-MIXING-ALPHA"] = args.alpha
    params["FORCE_EVAL-DFT-KPOINTS-SCHEME"] = args.kpoints_scheme

    params["MOTION-GEO_OPT-MAX_ITER"] = args.max_iter
    params["MOTION-GEO_OPT-OPTIMIZER"] = args.optimizer
    params["MOTION-GEO_OPT-TYPE"] = args.type
    params["MOTION-GEO_OPT-MAX_DR"] = args.max_dr
    params["MOTION-GEO_OPT-MAX_FORCE"] = args.max_force
    params["MOTION-GEO_OPT-RMS_DR"] = args.rms_dr
    params["MOTION-GEO_OPT-RMS_FORCE"] = args.rms_force

    task = opt_run()
    task.get_xyz(args.file)
    task.set_geo_opt()
    task.set_params(params=params)
    #task.geo_opt(directory=args.directory, mpi=args.mpi, runopt=args.runopt, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)

    if os.path.exists(args.directory):
        shutil.rmtree(args.directory)
    os.mkdir(args.directory)

    shutil.copyfile(task.force_eval.subsys.xyz.file, os.path.join(args.directory, task.force_eval.subsys.xyz.file))
    
    # 
    os.chdir(args.directory)
    
    with open("geo-opt.inp.template", 'w') as fout:
        task.glob.to_input(fout)
        task.force_eval.to_input(fout)
        task.motion.to_input(fout)


    # gen pbs script
    with open("geo-opt-tetragonal.pbs", 'w') as fout:
        fout.write("#!/bin/bash\n")
        fout.write("#PBS -N %s\n" % args.jobname)
        fout.write("#PBS -l nodes=%d:ppn=%d\n" % (args.nodes, args.ppn))
        fout.write("\n")
        fout.write("cd $PBS_O_WORKDIR\n")
        fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
        fout.write("\n")
        fout.write("# get begin and end line number of the cell block in geo-opt.inp.template\n")
        fout.write("cell_block_begin=`cat geo-opt.inp.template | grep -n \'&CELL\' | head -n 1 | cut -d \':\' -f1`\n")
        fout.write("cell_block_end=`cat geo-opt.inp.template | grep -n \'&END CELL\' | head -n 1 | cut -d \':\' -f1\n`")
        fout.write("\n")

        a = task.force_eval.subsys.xyz.cell[0][0]
        c = task.force_eval.subsys.xyz.cell[2][2]
        
        fout.write("v11=%f\n" % task.force_eval.subsys.xyz.cell[0][0])
        fout.write("v12=%f\n" % task.force_eval.subsys.xyz.cell[0][1])
        fout.write("v13=%f\n" % task.force_eval.subsys.xyz.cell[0][2])
        fout.write("v21=%f\n" % task.force_eval.subsys.xyz.cell[1][0])
        fout.write("v22=%f\n" % task.force_eval.subsys.xyz.cell[1][1])
        fout.write("v23=%f\n" % task.force_eval.subsys.xyz.cell[1][2])
        fout.write("v31=%f\n" % task.force_eval.subsys.xyz.cell[2][0])
        fout.write("v32=%f\n" % task.force_eval.subsys.xyz.cell[2][1])
        fout.write("v33=%f\n" % task.force_eval.subsys.xyz.cell[2][2])
        if args.na >= 2:
            # a is optimized
            fout.write("for a in `seq -w %f %f %f`\n" % (a-args.na/2*args.stepa, args.stepa, a+args.na/2*args.stepa))
            fout.write("do\n")
            if args.nc >= 2:
                # optimize both a and c
                fout.write("  for c in `seq -w %f %f %f`\n" % (c-args.nc/2*args.stepc, args.stepc, c+args.nc/2*args.stepc))
                fout.write("  do\n")
                fout.write("    cat geo-opt.inp.template | head -n +${cell_block_begin} > geo-opt-${a}-${c}.inp\n")
                fout.write("    cat >> geo-opt-${a}-${c}.inp <<EOF\n")
                fout.write("\t\t\tA ${a} 0.000000 0.000000\n")
                fout.write("\t\t\tB 0.000000 ${a} 0.000000\n")
                fout.write("\t\t\tC 0.000000 0.000000 ${c}\n")
                fout.write("\t\t\tPERIODIC XYZ\n")
                fout.write("EOF\n")
                fout.write("    cat geo-opt.inp.template | tail -n +${cell_block_end} >> geo-opt-${a}-${c}.inp\n")
                fout.write("    mpirun -np $NP -machinefile $PBS_NODEFILE cp2k.popt -in geo-opt-${a}-${c}.inp > geo-opt-${a}-${c}.out\n")
                fout.write("  done\n")
            else:
                # only optimize a
                fout.write("    cat geo-opt.inp.template | head -n +${cell_block_begin} > geo-opt-${a}.inp\n")
                fout.write("    cat >> geo-opt-${a}.inp <<EOF\n")
                fout.write("\t\t\tA ${a} 0.000000 0.000000\n")
                fout.write("\t\t\tB 0.000000 ${a} 0.000000\n")
                fout.write("\t\t\tC 0.000000 0.000000 ${v33}\n")
                fout.write("\t\t\tPERIODIC XYZ\n")
                fout.write("EOF\n")
                fout.write("    cat geo-opt.inp.template | tail -n +${cell_block_end} >> geo-opt-${a}.inp\n")
                fout.write("    mpirun -np $NP -machinefile $PBS_NODEFILE cp2k.popt -in geo-opt-${a}.inp > geo-opt-${a}.out\n")
            fout.write("done\n")
        else:
        # a is not optimized
            if args.nc >= 2:
                # only optimize c
                fout.write("for c in `seq -w %f %f %f`\n" % (c-args.nc/2*args.stepc, args.stepc, c+args.nc/2*args.stepc))
                fout.write("do\n")
                fout.write("  cat geo-opt.inp.template | head -n +${cell_block_begin} > geo-opt-${c}.inp\n")
                fout.write("  cat >> geo-opt-${c}.in<<EOF\n")
                fout.write("\t\t\tA ${v11} 0.000000 0.000000\n")
                fout.write("\t\t\tB 0.000000 ${v22} 0.000000\n")
                fout.write("\t\t\tC 0.000000 0.000000 ${c}\n")
                fout.write("\t\t\tPERIODIC XYZ\n")
                fout.write("EOF\n")
                fout.write("    cat geo-opt.inp.template | tail -n +${cell_block_end} >> geo-opt-${a}.inp\n")
                fout.write("    mpirun -np $NP -machinefile $PBS_NODEFILE cp2k.popt -in geo-opt-${a}.inp > geo-opt-${a}.out\n")
                fout.write("done\n")
            else:
                # neither a or c is optimized
                pass


    # generate result analysis script
    with open("get_energy.sh", 'w') as fout:
        fout.write("#!/bin/bash\n")
        # the comment
        if args.na >= 2 and args.nc >= 2:
            fout.write("cat > energy-latconst.data <<EOF\n")
            fout.write("# format: a c energy(Ry)\n")
            fout.write("EOF\n")
        if args.na >= 2 and args.nc < 2:
            fout.write("cat > energy-latconst.data <<EOF\n")
            fout.write("# format: a energy(Ry)\n")
            fout.write("EOF\n")
        if args.na < 2 and args.nc >= 2:
            fout.write("cat > energy-latconst.data <<EOF\n")
            fout.write("# format: c energy(Ry)\n")
            fout.write("EOF\n")
        # end
        if args.na >= 2:
            # a is optimized
            fout.write("for a in `seq -w %f %f %f`\n" % (a-args.na/2*args.stepa, args.stepa, a+args.na/2*args.stepa))
            fout.write("do\n")
            if args.nc >= 2:
                # both a and c are optimized
                fout.write("for c in `seq -w %f %f %f`\n" % (c-args.nc/2*args.stepc, args.stepc, c+args.nc/2*args.stepc))
                fout.write("  do\n")
                fout.write("    energy=`cat geo-opt-${a}-${c}.out | grep 'ENERGY| Total FORCE_EVAL' | tail -n -1`\n")
                fout.write("    cat >> energy-latconst.data <<EOF\n")
                fout.write("${a} ${c} ${energy:48-1\n")
                fout.write("EOF\n")
                fout.write("  done\n")
            else:
                fout.write("  energy=`cat geo-opt-${a}.out | grep 'ENERGY| Total FORCE_EVAL' | tail -n -1`\n")
                fout.write("  cat >> energy-latconst.data <<EOF\n")
                fout.write("${a} ${energy:48-1}\n")
                fout.write("EOF\n")
            fout.write("done\n")
        else:
        # a is not optimized
            if args.nc >= 2:
                # only c is optimized
                fout.write("for c in `seq -w %f %f %f`\n" % (c-args.nc/2*args.stepc, args.stepc, c+args.nc/2*args.stepc))
                fout.write("do\n")
                fout.write("  energy=`cat geo-opt-${c}.out | grep 'ENERGY| Total FORCE_EVAL' | tail -n -1`\n")
                fout.write("  cat >> energy-latconst.data <<EOF\n")
                fout.write("${c} ${energy:48-1}\n")
                fout.write("EOF\n")
                fout.write("done\n")
            else:
                # neither a nor c is optimized
                pass

    os.chdir("../")


    server_handle(auto=args.auto, directory=args.directory, jobfilebase="geo-opt-tetragonal", server=args.server)
        
