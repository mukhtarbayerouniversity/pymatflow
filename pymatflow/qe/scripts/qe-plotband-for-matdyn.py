#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import argparse

from pymatflow.qe.dfpt import dfpt_run
from pymatflow.remote.server import server_handle

"""
usage:
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("-d", "--directory", help="directory for the static running", type=str, default="tmp-qe-static")
    parser.add_argument("--mpi", help="MPI commadn", type=str, default="")
    parser.add_argument("-f", "--file", help="the xyz file", type=str)
    parser.add_argument("--runopt", help="gen, run, or genrun", type=str, default="genrun")
   
    # --------------------------------------------------------------
    # for plotband
    # --------------------------------------------------------------
    parser.add_argument("--freq-min", type=float, default=0,
            help="range of frequencies for visualization")
    parser.add_argument("--freq-max", type=float, default=600,
            help="range of frequencies for visualization")
    parser.add_argument("--efermi", type=float, default=0,
            help="fermi energy level(only needed for band structure plot)")
    parser.add_argument("--freq-step", type=float, default=100.0,
            help="freq step")
    parser.add_argument("--freq-reference", type=float, default=0.0,
            help="freq reference")
   
    # -----------------------------------------------------------------
    #                      for server handling
    # -----------------------------------------------------------------
    parser.add_argument("--auto", type=int, default=0,
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing in remote server, 3: pymatflow used in server with direct submit, in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")
    parser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")
    parser.add_argument("--jobname", type=str, default="qe-plotband",
            help="jobname on the pbs server")
    parser.add_argument("--nodes", type=int, default=1,
            choices=[1],
            help="Nodes used in server")
    parser.add_argument("--ppn", type=int, default=1,
            choices=[1],
            help="ppn of the server, plotband.x is not parallelized so must use 1 node 1 ppn")



    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================
    args = parser.parse_args()
    xyzfile = args.file

    task = dfpt_run()
    task.get_xyz(args.file)
    task.plotband_for_matdyn(directory=args.directory, mpi=args.mpi, runopt=args.runopt, freq_min=args.freq_min, freq_max=args.freq_max, efermi=args.efermi, freq_step=args.freq_step, freq_reference=args.freq_reference, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)

    server_handle(auto=args.auto, directory=args.directory, jobfilebase="plotband", server=args.server)

