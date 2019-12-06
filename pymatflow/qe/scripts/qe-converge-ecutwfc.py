#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import argparse 

from pymatflow.qe.static import static_run
from pymatflow.remote.ssh import ssh
from pymatflow.remote.rsync import rsync

"""
usage qe-converge-ecutwfc.py -f xxx.py --range emin emax step
"""

control_params = {}
system_params = {}
electrons_params = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="directory of the calculation", type=str, default="tmp-qe-ecutwfc")
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)
    parser.add_argument("--runopt", help="gen run genrun", type=str, default="genrun")
    parser.add_argument("--range", help="ecutwfc test range", nargs='+', type=int)
    parser.add_argument("--kpoints-option", type=str, default="automatic", 
            choices=["automatic", "gamma"],
            help="Kpoints generation scheme option for the SCF or non-SCF calculation")
    parser.add_argument("-k", "--kpoints", type=str, default="1 1 1 0 0 0",
            help="Monkhorst-Pack kpoint grid, in format like '1 1 1 0 0 0'")
    parser.add_argument("--conv-thr", help="conv_thr", type=float, default=1.0e-6)

    parser.add_argument("--occupations", type=str, default="smearing",
            choices=["smearing", "tetrahedra", "tetrahedra_lin", "tetrahedra_opt", "fixed", "from_input"],
            help="Occupation method for the calculation.")
    
    parser.add_argument("--smearing", type=str, default="gaussian",
            choices=["gaussian", "methfessel-paxton", "marzari-vanderbilt", "fermi-dirac"],
            help="Smearing type for occupations by smearing, default is gaussian in this script")

    parser.add_argument("--degauss", type=float, default=0.001,
            help="Value of the gaussian spreading (Ry) for brillouin-zone integration in metals.(defualt: 0.001 Ry)")

    parser.add_argument("--vdw-corr", type=str, default="none",
            choices=["dft-d", "dft-d3", "ts", "xdm"],
            help="Type of Van der Waals correction in the calculation")

    # for server
    parser.add_argument("--auto", type=int, default=0,
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, in order use auto=1, 2, you must make sure there is a working ~/.emuhelper/server.conf")
    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================
    args = parser.parse_args()
    xyzfile = args.file
    system_params["occupations"] = args.occupations
    system_params["smearing"] = args.smearing
    system_params["degauss"] = args.degauss
    system_params["vdw_corr"] = args.vdw_corr
    electrons_params["conv_thr"] = args.conv_thr
    kpoints_mp = [int(args.kpoints.split()[i]) for i in range(6)]
    
    task = static_run(xyzfile)
    task.converge_ecutwfc(args.range[0], args.range[1], args.range[2], directory=args.directory, control=control_params, system=system_params, electrons=electrons_params, kpoints_option=args.kpoints_option, kpoints_mp=kpoints_mp, runopt=args.runopt)   

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
        ctl.submit(workdir=args.directory, jobfile="converge-ecutwfc.in.sub")
