#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import argparse

from emuhelper.qe.neb import neb_run

"""
usage:
    qe-neb.py -f xxx.xyz -k '2 2 2 0 0 0' --ecutwfc 100
"""


control_params = {}
system_params = {}
electrons_params = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="directory of the calculation", type=str, default="tmp-qe-neb")
    parser.add_argument("--image1", help="the first image xyz file", type=str)
    parser.add_argument("--image2", help="the intermediate image xyz file", type=str)
    parser.add_argument("--image3", help="the last image xyz file", type=str)
    parser.add_argument("--ecutwfc", help="ecutwfc, default value: 100 Ry", type=int, default=100)
    parser.add_argument("-k", "--kpoints", help="set kpoints like '1 1 1 0 0 0'", type=str, default="1 1 1 0 0 0")
 
    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================   
    args = parser.parse_args()
    directory = args.directory
    image1 = args.image1
    image2 = args.image2
    image3 = args.image3
    system_params["ecutwfc"] = args.ecutwfc
    kpoints_mp = [int(args.kpoints.split()[i]) for i in range(6)]
    

    task = neb_run(image1, image2, image3)
    task.neb(directory=directory, runopt="genrun", control=control_params, system=system_params, electrons=electrons_params, kpoints_mp=kpoints_mp)