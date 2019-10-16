#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import argparse

from emuhelper.qe.static import static_run

"""
usage qe-converge-kpoints.py -f xxx.xyz --range nk_min nk_max step
"""

control_params = {}
system_params = {}
electrons_params = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)
    parser.add_argument("--ecutwfc", help="better specify a converged ecutwfc", type=int, default=100)
    parser.add_argument("--range", help="nk_min nk_max step", nargs='+', type=int)

    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================
    args = parser.parse_args()
    xyzfile = args.file
    system_params["ecutwfc"] = args.ecutwfc

    task = static_run(xyzfile)
    task.converge_kpoints(args.range[0], args.range[1], args.range[2], control=control_params, system=system_params, electrons=electrons_params, runopt="genrun")