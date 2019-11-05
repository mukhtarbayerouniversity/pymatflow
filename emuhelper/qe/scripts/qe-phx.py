#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import argparse

from emuhelper.qe.static import static_run

"""
usage:
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("-d", "--directory", help="directory for the static running", type=str, default="tmp-qe-static")
    parser.add_argument("--mpi", help="MPI commadn", type=str, default="")
    parser.add_argument("-f", "--file", help="the xyz file", type=str)
    parser.add_argument("--runopt", help="gen, run, or genrun", type=str, default="genrun")
    
    # for phx
    parser.add_argument("--phx-qpoints", type=int, nargs="+",
            default=[2, 2, 2],
            help="qpoints for ph.x")

    # for q2r
    parser.add_argument("--zasr", type=str, default="simple",
            hep="sum rule")

    # for matdyn.x
    parser.add_argument("--asr", type=str, default='simple',
            help="type of sum rule")
    parser.add_argument("--nqpoints", type=int, default=2,
            help="number of qpoints")
    parser.add_argument("--matdyn-qpoints", type=float, nargs="+",
            default= [0.0, 0.0, 0.0, 0.0, 0.012658, 0.0, 0.0, 0.012658],
            help="matdyn qpoints")

    # for plotband
    parser.add_argument("--freq-min", type=float, default=0,
            help="range of frequencies for visualization")
    parser.add_argument("--freq-max", type=float, default=600,
            help="range of frequencies for visualization")

    # ==========================================================
    # transfer parameters from the arg parser to opt_run setting
    # ==========================================================
    args = parser.parse_args()
    xyzfile = args.file

    matdyn_qpoints = []
    for i in range(0, len(args.matdyn_qpoints), 4):
        matdyn_qpoints.append([args.matdyn_qpoints[i], args.matdyn_qpoints[i+1], args.matdyn_qpoints[i+2], args.matdyn_qpoints[i+3]])



    task = static_run(xyzfile)
    task.phx_qmesh(directory=args.directory, mpi=args.mpi, runopt=args.runopt, qpoints=args.phx_qpoints)
    task.q2r(directory=args.directory, mpi=args.mpi, runopt=args.runopt, zasr=args.zasr)
    task.matdyn(directory=args.directory, mpi=args.mpi, runopt=args.runopt, asr=args.asr, nqpoints=args.nqpoints, qpoints=matdyn_qpoints)
    task.plotband(directory=args.directory, mpi=args.mpi, runopt=args.runopt, freq_min=args.freq_min, freq_max=args.freq_max)
