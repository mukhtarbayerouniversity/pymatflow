#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import argparse

from emuhelper.cp2k.static import static_run

"""
usage:
    cp2k-scf.py -f xxx.xyz
"""


force_eval = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="directory of the calculation", type=str, default="tmp-cp2k-static")
    parser.add_argument("-f", "--file", help="the xyz file name", type=str)
    parser.add_argument("-p", "--printout-option", nargs="+", type=int,
            default=[],
            help="Properties printout option(0, 1, 2 implemented now), you can also activate multiple prinout-option at the same time")
    parser.add_argument("--xc-functional", type=str, default="PBE",
            help="XC_FUNCTIONAL type")
    parser.add_argument("--cutoff", type=int, default=100,
            help="CUTOFF, default value: 100 Ry")
    parser.add_argument("--rel-cutoff", type=int, default=60,
            help="REL_CUTOFF, default value: 60 Ry")
    parser.add_argument("-k", "--kpoints", help="set kpoints like '3 3 3 0 0 0'", type=str, default="3 3 3 0 0 0")
    parser.add_argument("--added-mos", help="ADDED_MOS for SCF", type=int, default=0)
    parser.add_argument("--smear", type=bool, default=False,
            choices=[True, False],
            help="switch on or off smearing for occupation")
    parser.add_argument("--smear-method", help="smearing type: FERMI_DIRAC, ENERGY_WINDOW", type=str, default="FERMI_DIRAC")
    parser.add_argument("--electronic-temp", help="ELECTRON_TEMPERATURE for FERMI_DIRAC SMEAR", type=float, default=300)
    parser.add_argument("--window-size", help="Size of the energy window centred at the Fermi level for ENERGY_WINDOW type smearing", type=float, default=0)
    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================   
    args = parser.parse_args()
    directory = args.directory
    xyzfile = args.file
    kpoints_mp = [int(args.kpoints.split()[i]) for i in range(6)]
    force_eval["DFT-MGRID-CUTOFF"] = args.cutoff
    force_eval["DFT-MGRID-REL_CUTOFF"] = args.rel_cutoff
    force_eval["DFT-XC-XC_FUNCTIONAL"] = args.xc_functional
    force_eval["DFT-SCF-ADDED_MOS"] = args.added_mos
    force_eval["DFT-SCF-SMEAR"] = args.smear
    force_eval["DFT-SCF-SMEAR-METHOD"] = args.smear_method
    force_eval["DFT-SCF-SMEAR-ELECTRONIC_TEMPERATURE"] = args.electronic_temp
    force_eval["DFT-SCF-SMEAR-WINDOW_SIZE"] = args.window_size

    task = static_run(xyzfile)
    task.scf_restart(directory=directory, runopt="genrun", force_eval=force_eval)
