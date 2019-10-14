#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import argparse

from emuhelper.qe.opt import opt_run

"""
usage: qe-vc-relax.py -f xxx.xyz
"""

system_params = {}
electrons_params = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)
    parser.add_argument("--ecutwfc", help="ecutwfc", type=int, default=100)
    parser.add_argument("-k", "--kpoints", help="set kpoints like '1 1 1 0 0 0'", type=str, default="1 1 1 0 0 0")
    parser.add_argument("--conv_thr", help="conv_thr for scf", type=float, default=1.0e-6)
   
    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================
    args = parser.parse_args()
    xyzfile = args.file
    system_params["ecutwfc"] = args.ecutwfc
    electrons_params["conv_thr"] = args.conv_thr
    kpoints_mp = [int(args.kpoints.split()[i]) for i in range(6)]

    task = opt_run(xyzfile)
    task.vc_relax(runopt="genrun", system=system_params, electrons=electrons_params, kpoints_mp=kpoints_mp)
