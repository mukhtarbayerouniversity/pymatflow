#!/usr/bin/evn python
# _*_ coding:utf-8 _*_

import argparse

from pymatflow.siesta.phonopy import phonopy_run
from pymatflow.remote.ssh import ssh
from pymatflow.remote.rsync import rsync

"""
usage:
"""


electrons = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="directory of the calculation", type=str, default="tmp-siesta-phonopy")
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)

    parser.add_argument("--runopt", type=str, default="genrun", 
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    parser.add_argument("--mpi", help="MPI command", type=str, default="")
    parser.add_argument("--meshcutoff", help="MeshCutoff (Ry)", type=int, default=200)
    parser.add_argument("--solution-method", help="SolutionMethod(diagon, OMM, OrderN, PEXSI)", type=str, default="diagon")
    parser.add_argument("--functional", help="XC.functional", type=str, default="GGA")
    parser.add_argument("--authors", help="XC.authors", type=str, default="PBE")
    parser.add_argument("--tolerance", help="DM.Tolerance", type=float, default=1.0e-6)
    parser.add_argument("--numberpulay", help="DM.NumberPulay", type=int ,default=8)
    parser.add_argument("--mixing", help="DM.MixingWeight", type=float, default=0.1)

    parser.add_argument("--kpoints-mp", type=int, nargs="+",
            default=[3, 3, 3],
            help="set kpoints like '3 3 3'")

    parser.add_argument("--occupation", help="OccupationFunction(FD or MP)", type=str, default="FD")
    parser.add_argument("--electronic-temperature", help="Electronic Temperature", type=int, default=300)
    #------------------------------------------------------------------------------------------------

    # -------------------------------
    #      Phonopy
    # -------------------------------
    parser.add_argument("-n", "--supercelln", type=int, nargs="+",
            default=[1, 1,1],
            help="supercell option for phonopy, like '2 2 2'")

    # ----------------------------
    # for server
    # ----------------------------
    parser.add_argument("--auto", type=int, default=0,
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, in order use auto=1, 2, you must make sure there is a working ~/.emuhelper/server.conf")

    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================   
    args = parser.parse_args()
    xyzfile = args.file
    directory = args.directory
    
    electrons["MeshCutoff"] = args.meshcutoff
    electrons["SolutionMethod"] = args.solution_method
    electrons["XC.funtional"] = args.functional
    electrons["XC.authors"] = args.authors
    electrons["DM.Tolerance"] = args.tolerance
    electrons["DM.NumberPulay"] = args.numberpulay
    electrons["DM.MixingWeight"] = args.mixing
    electrons["OccupationFunction"] = args.occupation
    electrons["ElectronicTemperature"] = args.electronic_temperature


    task = phonopy_run()
    task.get_xyz(xyzfile)

    task.phonopy(directory=directory, runopt=args.runopt, mpi=args.mpi, electrons=electrons, kpoints_mp=args.kpoints_mp, supercelln=args.supercelln)

    # server handle
    if args.auto == 0:
        pass
    elif args.auto == 1:
        mover = rsync()
        mover.get_info(os.path.join(os.path.expanduser("~"), ".emuhelper/server.conf"))
        mover.copy_default(source=os.path.abspath(args.directory))
    elif args.auto == 2:
        mover = rsync()
        mover.get_info(os.path.join(os.path.expanduser("~"), ".emuhelper/server.conf"))
        mover.copy_default(source=os.path.abspath(args.directory))
        ctl = ssh()
        ctl.get_info(os.path.join(os.path.expanduser('~'), ".emuhelper/server.conf"))
        ctl.login()
        ctl.submit(workdir=args.directory, jobfile="phonpy.sub")
