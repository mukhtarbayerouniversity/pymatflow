#!/usr/bin/env python

import os
import sys
import argparse



def get_kpath(kpath_manual=None, kpath_file=None):
    """
    :param kpath_manual: manual input kpath like --kpath '0.000000 0.000000 0.000000 GAMMA 5' '0.500000 0.000000 0.000000 X 5' '0.0000 0.000 0.50000 A |' '0.5 0.5 0.5 R '
    :param kpath_file: manual input kpath read from the file
    :return kpath or None(when kpath_manual and kpath_file are both None)
    """
    # dealing with standard kpath
    kpath = None
    if kpath_manual != None:
        # kpath from script argument args.kpath
        kpath = []
        for kpoint in kpath_manual:
            if kpoint.split()[4] != "|":
                kpath.append([
                    float(kpoint.split()[0]),
                    float(kpoint.split()[1]),
                    float(kpoint.split()[2]),
                    kpoint.split()[3].upper(),
                    int(kpoint.split()[4]),
                    ])
            elif kpoint.split()[4] == "|":
                kpath.append([
                    float(kpoint.split()[0]),
                    float(kpoint.split()[1]),
                    float(kpoint.split()[2]),
                    kpoint.split()[3].upper(),
                    "|",
                    ])
        return kpath
    elif kpath_file != None:
        # kpath read from file specified by kpath_file
        # file is in format like this
        """
        5
        0.0 0.0 0.0 #GAMMA 15
        x.x x.x x.x #XXX |
        x.x x.x x.x #XXX 10
        x.x x.x x.x #XXX 15
        x.x x.x x.x #XXX 20
        """
        # if there is a '|' behind the label it means the path is
        # broken after that point!!!
        kpath = []
        with open(kpath_file, 'r') as fin:
            lines = fin.readlines()
        nk = int(lines[0])
        for i in range(nk):
            if lines[i+1].split("\n")[0].split()[4] != "|":
                kpath.append([
                    float(lines[i+1].split()[0]),
                    float(lines[i+1].split()[1]),
                    float(lines[i+1].split()[2]),
                    lines[i+1].split()[3].split("#")[1].upper(),
                    int(lines[i+1].split()[4]),
                    ])
            elif lines[i+1].split("\n")[0].split()[4] == "|":
                kpath.append([
                    float(lines[i+1].split()[0]),
                    float(lines[i+1].split()[1]),
                    float(lines[i+1].split()[2]),
                    lines[i+1].split()[3].split("#")[1].upper(),
                    '|',
                    ])
        return kpath
    else:
        pass
    # -------------------------------------------------------------------



def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="driver", title="subcommands", description="choose one and only one calculator")

    # --------------------------------------------------------------------------
    # Abinit
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("abinit", help="using abinit as calculator")

    subparser.add_argument("-r", "--runtype", type=int, default="static",
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            help="choices of runtype. 0->static_run; 1->optimization; 2->cubic-opt; 3->hexagonal-opt; 4->tetragonal-opt; 5->dfpt-elastic-piezo-dielec; 6->dfpt-phonon; 7->phonopy")

    subparser.add_argument("-d", "--directory", type=str, default="matflow-running",
            help="Directory to do the calculation")

    # structure file: either xyz or cif. they are exclusive
    # actually this can be put in the main subparser, but it will make the command not like git sub-cmmand
    # so we put them in every subsubparser
    structfile = subparser.add_mutually_exclusive_group(required=True) # at leaset one of cif and xyz is provided
    # argparse will make sure only one of argument in structfile(xyz, cif) appear on command line
    structfile.add_argument("--xyz", type=str, default=None,
            help="The xyz structure file with second line specifying cell parameters")

    structfile.add_argument("--cif", type=str, default=None,
            help="The cif structure file")

    subparser.add_argument("--chkprim", type=int, default=1,
            choices=[0, 1],
            help="check whether the input cell is primitive. if your cell is not primitive, set chkprim to 0. for more information, refer to https://docs.abinit.org/variables/gstate/#chkprim")

    subparser.add_argument("--kpath-manual", type=str, nargs="+", default=None,
            help="manual input kpath for band structure calculation")

    subparser.add_argument("--kpath-file", type=str,
            help="file to read the kpath for band structure calculation")

    subparser.add_argument("--iscf", type=int, default=7,
            choices=[0, 1, 2, 3, 4, 5, 7, 12, 13, 14, 15, 17],
            help="set scf or nscf type. for more information, refer to https://docs.abinit.org/variables/basic/#iscf")

    subparser.add_argument("--ecut", type=int, default=15,
            help="Kinetic energy cutoff for wave functions in unit of Hartree, default value: 15 Hartree. for more information, refer to https://docs.abinit.org/variables/basic/#ecut")

    subparser.add_argument("--ixc", type=int, default=11,
            choices=[1, 2, 3 ,4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 40, 41, 42],
            help="type of exchage-correlation functional. for more information, refer to https://docs.abinit.org/variables/basic/#ixc")

    subparser.add_argument("--kptopt", type=int, default=1,
            choices=[1],
            help="Kpoints Generation scheme option: 0, 1, 2, 3, 4 or a negative value. for more information, refer to https://docs.abinit.org/variables/basic/#kptopt")

    subparser.add_argument("--ngkpt", nargs="+", type=int,
            default=[1, 1, 1],
            help="number of grid points for kpoints generation. for more information, refer to https://docs.abinit.org/variables/basic/#ngkpt")

    # electron occupation
    subparser.add_argument("--occopt", type=int, default=3,
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            help="Controls how input parameters nband, occ, and wtk are handled. for more information, refer to https://docs.abinit.org/variables/basic/#occopt")

    subparser.add_argument("--nband", type=int, nargs="+", default=None,
            help="Gives number of bands, occupied plus possibly unoccupied, for which wavefunctions are being computed along with eigenvalues. for more information, refer to https://docs.abinit.org/variables/basic/#nband")

    subparser.add_argument("--occ", nargs="+", type=float, default=None,
            help="Gives occupation numbers for all bands in the problem. Needed if occopt == 0 or occopt == 2. Ignored otherwise. Also ignored when iscf = -2. refer to https://docs.abinit.org/variables/gstate/#occ")

    # magnetic related parameters
    subparser.add_argument("--nsppol", type=int, default=None,
            choices=[1, 2],
            help="Give the number of INDEPENDENT spin polarisations, for which there are non- related wavefunctions. Can take the values 1 or 2. for more information, refer to https://docs.abinit.org/variables/basic/#nsppol")

    # vdw related parameters
    subparser.add_argument("--vdw-xc", type=int, default=None,
            choices=[0, 1, 2, 5, 6, 7, 10, 11, 14],
            help="Van Der Waals exchange-correlation functional. 0: no correction, 1: vdW-DF1, 2: vdW-DF2, 5: DFT-D2, 6: DFT-D3, 7: DFT-D3(BJ). for more information, refer to https://docs.abinit.org/variables/vdw/#vdw_xc")

    subparser.add_argument("--vdw-tol", type=float,
            default=None,
            help="Van Der Waals tolerance, only work when vdw_xc == 5 or 6 or 7. to be included in the potential a pair of atom must have contribution to the energy larger than vdw_tol. default value is 1.0e-10. fore more information, refer to https://docs.abinit.org/variables/vdw/#vdw_tol")

    subparser.add_argument("--prtden", type=int ,default=1,
            choices=[0, 1],
            help="print the density. for more information, refer to https://docs.abinit.org/variables/files/#prtden")

    subparser.add_argument("--prtdos", type=int, default=None,
            choices=[0, 1, 2, 3],
            help="can be 0, 1, 2, 3. for more information, refer to https://docs.abinit.org/variables/files/#prtdos")

    subparser.add_argument("--properties", nargs="+", type=int,
            default=[],
            help="options for properties calculation")

    # -----------------------------------------------------------
    #                        ions moving related parameters
    # -----------------------------------------------------------

    subparser.add_argument("--ionmov", type=int, default=3,
            choices=[2, 3, 4, 5],
            help="type of ionmov algorithm. fore more information, refer to https://docs.abinit.org/variables/rlx/#ionmov")

    subparser.add_argument("--optcell", type=int,
            choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            default=0,
            help="whether to optimize the cell shape and dimension. fore more information, refer to https://docs.abinit.org/variables/rlx/#optcell")

    subparser.add_argument("--chkdilatmx", type=int, default=None,
            choices=[0, 1],
            help="check dilatmx. fore more information, refer to https://docs.abinit.org/variables/rlx/#chkdilatmx")

    subparser.add_argument("--dilatmx", type=float, default=None,
            help="lattice dilation maximal value. fore more information, refer to https://docs.abinit.org/variables/rlx/#dilatmx")

    subparser.add_argument("--ecutsm", type=float, default=None,
            help="when optcell != 0, must specify encutsm larser than zero. for more information refer to https://docs.abinit.org/variables/rlx/#ecutsm")

    # ------------------------------------------------
    # na stepa nc stepc
    # ------------------------------------------------
    subparser.add_argument("--na", type=int, default=10,
            help="number of a to run")
    subparser.add_argument("--stepa", type=float, default=0.05,
            help="step of a in unit of Angstrom")
    subparser.add_argument("--nc", type=int, default=10,
            help="number of c to run")
    subparser.add_argument("--stepc", type=float, default=0.05,
            help="step of c in unit of Angstrom")

    # run option
    subparser.add_argument("--runopt", type=str, default="gen",
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    subparser.add_argument("--auto", type=int, default=3,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")

    subparser.add_argument("--supercell-n", type=int, nargs="+",
            default=[1, 1, 1],
            help="supercell build for phonopy.")

    # run params
    # -----------------------------------------------------------------

    subparser.add_argument("--mpi", type=str, default="",
            help="MPI command: like 'mpirun -np 4'")

    subparser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")

    subparser.add_argument("--jobname", type=str, default="matflow-job",
            help="jobname on the pbs server")

    subparser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")

    subparser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")


    # --------------------------------------------------------------------------
    # CP2K
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("cp2k", help="using cp2k as calculator")

    subparser.add_argument("-r", "--runtype", type=int, default="static",
            choices=[0, 1, 2, 3, 4 ,5, 6],
            help="choices of runtype. 0->static_run; 1->geo-opt; 2->cell-opt; 3->cubic-cell; 4->hexagonal-cell; 5->tetragonal-cell; 6->phonopy")

    subparser.add_argument("-d", "--directory", type=str, default="matflow-running",
            help="Directory to do the calculation")


    # structure file: either xyz or cif. they are exclusive
    # actually this can be put in the main subparser, but it will make the command not like git sub-cmmand
    # so we put them in every subsubparser
    structfile = subparser.add_mutually_exclusive_group(required=True) # at leaset one of cif and xyz is provided
    # argparse will make sure only one of argument in structfile(xyz, cif) appear on command line
    structfile.add_argument("--xyz", type=str, default=None,
            help="The xyz structure file with second line specifying cell parameters")

    structfile.add_argument("--cif", type=str, default=None,
            help="The cif structure file")


    # force_eval/dft related parameters

    subparser.add_argument("--qs-method", type=str, default="gpw",
            choices=["am1", "dftb", "gapw", "gapw_xc", "gpw", "lrigpw", "mndo", "mndod",
                "ofgpw", "pdg", "pm3", "pm6", "pm6-fm", "pnnl", "rigpw", "rm1"],
            help="dft-qs-method: specify the electronic structure method")

    subparser.add_argument("--eps-scf", type=float, default=1.0e-6,
            help="dft-scf-eps_scf")

    subparser.add_argument("--xc-functional", type=str, default="pbe",
            help="dft-xc-xc_functional: LYP, PADE, PBE, PW92, TPSS, XGGA, XWPBE, etc.")

    subparser.add_argument("--cutoff", type=int, default=100,
            help="CUTOFF, default value: 100 Ry")

    subparser.add_argument("--rel-cutoff", type=int, default=60,
            help="REL_CUTOFF, default value: 60 Ry")

    subparser.add_argument("-k", "--kpoints-scheme", type=str,
            default="GAMMA",
            help="DFT-KPOINTS-SCHEME(str): can be NONE, GAMMA, MONKHORST-PACK, MACDONALD, GENERAL. when you set MONKHORST-PACK, you should also add the three integers like 'monkhorst-pack 3 3 3'")

    subparser.add_argument("--kpath-manual", type=str, nargs="+", default=None,
            help="manual input kpath for band structure calculation")

    subparser.add_argument("--kpath-file", type=str,
            help="file to read the kpath for band structure calculation")

    subparser.add_argument("--diag", type=str, default="TRUE",
            choices=["TRUE", "FALSE", "true", "false"],
            help="whether choosing tranditional diagonalization for SCF")

    subparser.add_argument("--ot", type=str, default="FALSE",
            choices=["TRUE", "FALSE", "true", "false"],
            help="whether choosing orbital transformation for SCF")

    subparser.add_argument("--alpha", type=float, default=0.4,
            help="DFT-SCF-MIXING-ALPHA")

    subparser.add_argument("--smear", type=str, default="FALSE",
            choices=["TRUE", "FALSE", "true", "false"],
            help="switch on or off smearing for occupation")

    subparser.add_argument("--smear-method", type=str, default="FERMI_DIRAC",
            help="smearing type: FERMI_DIRAC, ENERGY_WINDOW")

    subparser.add_argument("--added-mos", type=int, default=0,
            help="ADDED_MOS for SCF")

    subparser.add_argument("--electronic-temp", type=float, default=300,
            help="ELECTRON_TEMPERATURE for FERMI_DIRAC SMEAR")

    subparser.add_argument("--window-size", type=float, default=0,
            help="Size of the energy window centred at the Fermi level for ENERGY_WINDOW type smearing")

    subparser.add_argument("--ls-scf", type=str, default="false",
            choices=["true", "false", "true", "false"],
            help="dft-ls_scf: use linear scaling scf method")

    # vdw correction related
    subparser.add_argument("--usevdw", type=str, default="FALSE",
            choices=["TRUE", "FALSE", "true", "false"],
            help="whether to use VDW correction")

    subparser.add_argument("--vdw-potential-type", type=str, default="PAIR_POTENTIAL",
            choices=["PAIR_POTENTIAL", "NON_LOCAL", "NONE"],
            help="DFT-XC-VDW_POTENTIAL-POTENTIAL_TYPE: PAIR_POTENTIAL, NON_LOCAL")

    subparser.add_argument("--pair-type", type=str, default="DFTD3",
            choices=["DFTD2", "DFTD3", "DFTD3(BJ)"],
            help="VDW PAIR_POTENTIAL type: DFTD2, DFTD3, DFTD3(BJ)")

    subparser.add_argument("--r-cutoff", type=float, default=1.05835442E+001,
            help="DFT-XC-VDW_POTENTIAL-PAIR_POTENTIAL: Range of potential. The cutoff will be 2 times this value")

    subparser.add_argument("-p", "--printout-option", nargs="+", type=int,
            default=[],
            choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            help=
            """
            Properties printout option, you can also activate multiple prinout-option at the same time.
            1: printout pdos
            2: printout band
            3: printout electron densities
            4: printout electron local function(ELF)
            5: printout molecular orbitals
            6: printout molecular orbital cube files
            7: printout mulliken populaltion analysis
            8: printout cubes for generation of STM images
            9: printout cube file with total density(electrons+atomic core)
           10: printout v_hartree_cube
           11: printout v_xc_cube
           12: printout xray_diffraction_spectrum
           13: request a RESP fit of charges.
           default is no printout of these properties.
           """)

    subparser.add_argument("--dft-print-elf-cube-stride", type=int, nargs="+",
            default=[1, 1, 1],
            help="DFT-PRINT-ELF_CUBE-STRIDE")

    subparser.add_argument("--dft-print-e-density-cube-stride", type=int, nargs="+",
            default=[1, 1, 1],
            help="DFT-PRINT-E_DENSITY_CUBE-STRIDE")

    # ------------------------------------------------------------------
    #                    force_eval/properties related parameters
    # ------------------------------------------------------------------

    subparser.add_argument("--properties-resp-slab-sampling-range", type=float, nargs="+",
            default=[0.3, 3.0],
            help="PROPERTIES-RESP-SLAB_SAMPLING-RANGE.")

    subparser.add_argument("--properties-resp-slab-sampling-surf-direction", type=str, default="Z",
            choices=["X", "Y", "Z", "x", "y", "z", "-X", "-Y", "-Z", "-x", "-y", "-z"],
            help="PROPERTIES-RESP-SLAB_SAMPLING-SURF_DIRECTION.")

    subparser.add_argument("--properties-resp-slab-sampling-atom-list", type=int, nargs="+",
            default=[1],
            help="PROPERTIES-RESP-SLAB_SAMPLING-ATOM_LIST")

    # --------------------------------------------------------------------------
    # MOTION/CELL_OPT related parameters
    # --------------------------------------------------------------------------
    subparser.add_argument("--cell-opt-optimizer", type=str, default="BFGS",
            help="optimization algorithm for geometry optimization: BFGS, CG, LBFGS")

    subparser.add_argument("--cell-opt-max-iter", type=int, default=200,
            help="maximum number of geometry optimization steps.")

    subparser.add_argument("--cell-opt-type", type=str, default="DIRECT_CELL_OPT",
            choices=["DIRECT_CELL_OPT", "GEO_OPT", "MD"],
            help="specify which kind of geometry optimization to perform: DIRECT_CELL_OPT(default), GEO_OPT, MD")

    subparser.add_argument("--cell-opt-max-dr", type=float, default=3e-3,
            help="Convergence criterion for the maximum geometry change between the current and the last optimizer iteration.")

    subparser.add_argument("--cell-opt-max-force", type=float, default=4.50000000E-004,
            help="Convergence criterion for the maximum force component of the current configuration.")

    subparser.add_argument("--cell-opt-rms-dr", type=float, default=1.50000000E-003,
            help="Convergence criterion for the root mean square (RMS) geometry change between the current and the last optimizer iteration.")

    subparser.add_argument("--cell-opt-rms-force", type=float, default=3.00000000E-004,
            help="Convergence criterion for the root mean square (RMS) force of the current configuration.")

    subparser.add_argument("--cell-opt-pressure-tolerance", type=float, default=1.00000000E+002,
            help="Specifies the Pressure tolerance (compared to the external pressure) to achieve during the cell optimization.")


    # --------------------------------------------------------------------------
    # MOTION/GEO_OPT related parameters
    # --------------------------------------------------------------------------
    subparser.add_argument("--geo-opt-optimizer", type=str, default="BFGS",
            help="optimization algorithm for geometry optimization: BFGS, CG, LBFGS")

    subparser.add_argument("--geo-opt-max-iter", type=int, default=200,
            help="maximum number of geometry optimization steps.")

    subparser.add_argument("--geo-opt-type", type=str, default="MINIMIZATION",
            help="specify which kind of geometry optimization to perform: MINIMIZATION(default), TRANSITION_STATE")

    subparser.add_argument("--geo-opt-max-dr", type=float, default=3e-3,
            help="Convergence criterion for the maximum geometry change between the current and the last optimizer iteration.")

    subparser.add_argument("--geo-opt-max-force", type=float, default=4.50000000E-004,
            help="Convergence criterion for the maximum force component of the current configuration.")

    subparser.add_argument("--geo-opt-rms-dr", type=float, default=1.50000000E-003,
            help="Convergence criterion for the root mean square (RMS) geometry change between the current and the last optimizer iteration.")

    subparser.add_argument("--geo-opt-rms-force", type=float, default=3.00000000E-004,
            help="Convergence criterion for the root mean square (RMS) force of the current configuration.")

    # na nc stepa stepc
    # -----------------------------------------
    subparser.add_argument("--na", type=int, default=10,
            help="number of a used")

    subparser.add_argument("--nc", type=int, default=10,
            help="number of c used")

    subparser.add_argument("--stepa", type=float, default=0.05,
            help="a step")

    subparser.add_argument("--stepc", type=float, default=0.05,
            help="c step")

    # run option
    subparser.add_argument("--runopt", type=str, default="gen",
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    subparser.add_argument("--auto", type=int, default=3,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")


    #                   PHONOPY related parameters
    # ------------------------------------------------------------------
    subparser.add_argument("--supercell-n", nargs="+", type=int, default=[1, 1, 1],
            help="Supercell for Phonopy calculation.")


    # -----------------------------------------------------------------
    #                      run params
    # -----------------------------------------------------------------

    subparser.add_argument("--mpi", type=str, default="",
            help="MPI command: like 'mpirun -np 4'")

    subparser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")

    subparser.add_argument("--jobname", type=str, default="matflow-job",
            help="jobname on the pbs server")

    subparser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")

    subparser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")


    # --------------------------------------------------------------------------
    # Quantum ESPRESSO
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("qe", help="using quantum espresso as calculator")

    subparser.add_argument("-r", "--runtype", type=int, default=0,
            choices=[0, 1, 2, 3, 4, 5, 6, 7, 8],
            help="choices of runtype. 0->static_run; 1->relax; 2->vc-relax; 3->cubic-cell; 4->hexagonal-cell; 5->tetragonal-cell; 6->neb; 7->dfpt; 8->phonopy")

    subparser.add_argument("-d", "--directory", type=str, default="matflow-running",
            help="Directory for the running.")

    # structure file: either xyz or cif. they are exclusive
    # actually this can be put in the main subparser, but it will make the command not like git sub-cmmand
    # so we put them in every subsubparser
    structfile = subparser.add_mutually_exclusive_group(required=True) # at leaset one of cif and xyz is provided
    # argparse will make sure only one of argument in structfile(xyz, cif) appear on command line
    structfile.add_argument("--xyz", type=str, default=None,
            help="The xyz structure file with second line specifying cell parameters")

    structfile.add_argument("--cif", type=str, default=None,
            help="The cif structure file")

    # -------------------------------------------------------------------
    #                       scf related parameters
    # -------------------------------------------------------------------
    subparser.add_argument("--ecutwfc",
            type=int, default=100)

    subparser.add_argument("--ecutrho", type=int, default=None,
            help="Kinetic energy cutoff for charge density and potential in unit of Rydberg, default value: None")

    subparser.add_argument("--kpoints-option", type=str, default="automatic",
            choices=["automatic", "gamma", "crystal_b"],
            help="Kpoints generation scheme option for the SCF or non-SCF calculation")

    subparser.add_argument("--kpoints-mp", type=int, nargs=6,
            default=[1, 1, 1, 0, 0, 0],
            help="Monkhorst-Pack kpoint grid, in format like --kpoints-mp 1 1 1 0 0 0")

    subparser.add_argument("--kpoints-mp-nscf", type=int, nargs=6,
            default=[3, 3, 3, 0, 0, 0],
            help="Monkhorst-Pack kpoint grid, in format like --kpoints-mp 3 3 3 0 0 0")

    subparser.add_argument("--kpath-manual", type=str, nargs="+", default=None,
            help="manual input kpath in crystal_b, like --kpath-manual '0.000000 0.000000 0.000000 GAMMA 5' '0.500000 0.000000 0.000000 X 5' '0.0000 0.000 0.50000 A |' '0.5 0.5 0.5 R '")

    subparser.add_argument("--kpath-file", type=str,
            help="manual input kpath in crystal_b read from the file")


    subparser.add_argument("--conv-thr", type=float, default=1.0e-6,
            help="the conv_thr for scf, when doing geometric optimization better use a strict covnergec for scf")

    subparser.add_argument("--occupations", type=str, default="smearing",
            choices=["smearing", "tetrahedra", "tetrahedra_lin", "tetrahedra_opt", "fixed", "from_input"],
            help="Occupation method for the calculation.")

    subparser.add_argument("--smearing", type=str, default="gaussian",
            choices=["gaussian", "methfessel-paxton", "marzari-vanderbilt", "fermi-dirac"],
            help="Smearing type for occupations by smearing, default is gaussian in this script")

    subparser.add_argument("--degauss", type=float, default=0.001,
            help="Value of the gaussian spreading (Ry) for brillouin-zone integration in metals.(defualt: 0.001 Ry)")

    subparser.add_argument("--nbnd", type=int, default=None,
            help="Number of electronic states (bands) to be calculated")

    subparser.add_argument("--tstress", type=str, default=".false.",
            choices=[".true.", ".false."],
            help="calculate stress. default=.false.")

    subparser.add_argument("--vdw-corr", help="vdw_corr = dft-d, dft-d3, ts-vdw, xdm", type=str, default="none")

    # magnetic related parameters
    subparser.add_argument("--nspin", type=int, default=None,
            choices=[1, 2],
            help="choose either 1 or 2, and 4 should not be used as suggested by pwscf official documentation.")

    subparser.add_argument("--starting-magnetization", type=float, nargs="+", default=None,
            help="starting_magnetization(i), i=1,ntyp -> Starting spin polarization on atomic type i in a spin polarized calculation. Values range between -1 (all spins down for the valence electrons of atom type i) to 1 (all spins up).")

    subparser.add_argument("--noncolin", type=str, default=None,
            choices=[".true.", ".false."],
            help="if .true. the program will perform a noncollinear calculation.")

    # ATOMIC_FORCES
    subparser.add_argument("--pressure", type=float, default=None,
            help="specify pressure acting on system in unit of Pa")
    subparser.add_argument("--pressuredir", type=str, default=None,
            choices=["x", "y", "z"],
            help="specify direction of pressure acting on system.")

    # projwfc
    subparser.add_argument("--projwfc-filpdos", type=str, default="projwfc",
            help="output projected dos file name")

    subparser.add_argument("--projwfc-ngauss", type=str, default="default",
            help="gaussian broadening type")

    subparser.add_argument("--projwfc-degauss", type=str, default='default',
            help="gaussian broadening")

    subparser.add_argument("--projwfc-emin", type=str, default='default',
            help="min energy for DOS")

    subparser.add_argument("--projwfc-emax", type=str, default='default',
            help="max energy for DOS")

    subparser.add_argument("--projwfc-deltae", type=str, default='default',
            help="DeltaE: energy grid step (eV)")

    # -----------------------------------------
    #         bands.x related parameters
    # -----------------------------------------
    subparser.add_argument("--lsym", type=str, default=".true.",
            choices=[".true.", ".false."],
            help="set lsym variable in bands.x input.")

    subparser.add_argument("--plot-num", type=int, nargs="+", default=[0],
            choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21],
            help="""
                type of analysis stored in the filplot file for later plot, 0: electron-pseudo-charge-density,
                    1: total-potential,
                    2: local-ionic-potential,
                    3: ldos,
                    4: local-density-of-electronic-entropy,
                    5: stm,
                    6: spin-polar,
                    7: molecular-orbitals,
                    8: electron-local-function,
                    9: charge-density-minus-superposition-of-atomic-densities,
                    10: ILDOS,
                    11: v_bare+v_H-potential,
                    12: sawtooth-electric-field-potential,
                    13: nocollinear-magnetization,
                    17: all-electron-charge-density-paw-only,
                    18: exchage-correlation-magnetic-field-noncollinear-case,
                    19: reduced-density-gradient,
                    20: product-of-charge-density-with-hessian,
                    21: all-electron-density-paw-only,""")

    subparser.add_argument("--iflag", type=int,
            default=3,
            choices=[0, 1, 2, 3, 4],
            help="dimension of the plot. 0: 1D plot of the spherical average, 1: 1D plot, 2: 2D plot, 3: 3D plot, 4: 2D polar plot on a sphere")

    subparser.add_argument("--output-format", type=int, default=5,
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            help="output file format for visualization. 0: gnuplot(1D), 1: no longer supported, 2: plotrho(2D), 3: XCRYSDEN(2d), 4: no longer supported, 5: XCRYSDEN(3D), 6: gaussian cube(3D), 7: gnuplot(2D)")


    # -------------------------------------------------------------------
    #               geometric optimization related parameters
    # -------------------------------------------------------------------
    subparser.add_argument("--etot-conv-thr",
            type=float, default=1.0e-4,
            help="convergence threshold of energy for geometric optimization")

    subparser.add_argument("--forc-conv-thr",
            type=float, default=1.0e-3,
            help="convergence threshold for force in optimization,(usually it is more important than energy)")

    subparser.add_argument("--nstep",
            type=int, default=50,
            help="maximum ion steps for geometric optimization")

    subparser.add_argument("--cell-dofree", type=str, default=None,
            choices=['all', 'ibrav', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', 'shape', 'volume', '2Dxy', '2Dshape', 'epitaxial_ab', 'epitaxial_ac', 'epitaxial_bc'],
            help="cell_dofree for &cell/")

    # na nc stepa stepc
    # -----------------------------------------
    subparser.add_argument("--na", type=int, default=10,
            help="number of a used")

    subparser.add_argument("--nc", type=int, default=10,
            help="number of c used")

    subparser.add_argument("--stepa", type=float, default=0.05,
            help="a step")

    subparser.add_argument("--stepc", type=float, default=0.05,
            help="c step")

    subparser.add_argument("--images", type=str, nargs="+",
            help="the image xyz file(--images first.xyz imtermediate-1.xyz intermediate-2.xyz ... last.xyz)")

    # run option
    subparser.add_argument("--runopt", type=str, default="gen",
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    subparser.add_argument("--auto", type=int, default=3,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")

    # params for neb namelist &path
    subparser.add_argument("--string-method", type=str, default="neb",
            help="string_method")

    subparser.add_argument("--nstep-path", type=int, default=100,
            help="nstep_path")

    subparser.add_argument("--opt-scheme", type=str, default="broyden",
            help="Specify the type of optimization scheme(sd, broyden, broyden2, quick-min, langevin)")

    subparser.add_argument("--num-of-images", type=int, default=5,
            help="number of total images(including the initial and final image). about how to set proper number of images: usually the inter-image distance between 1~2Bohr is OK")

    subparser.add_argument("--k-max", type=float, default=0.3e0,
            help="Set them to use a Variable Elastic Constants scheme elastic constants are in the range [ k_min, k_max  ], this is useful to rise the resolution around the saddle point")

    subparser.add_argument("--k-min", type=float, default=0.2e0,
            help="Set them to use a Variable Elastic Constants scheme elastic constants are in the range [ k_min, k_max  ], this is useful to rise the resolution around the saddle point")

    subparser.add_argument("--ci-scheme", type=str, default="auto",
            help="Specify the type of Climbing Image scheme(no-CI, auto, manual)")

    subparser.add_argument("--path_thr", type=float, default=0.05,
            help="path_thr")

    subparser.add_argument("--ds", type=float, default=1.e0, help="Optimisation step length ( Hartree atomic units )")

    subparser.add_argument("--first-last-opt", type=bool, default=False,
            help="whether to optimize the first and last image")


    # for phx
    # --------------------------------------------------------------
    subparser.add_argument("--tr2-ph", type=float, default=1.0e-14,
            help="threshold for self-consistency.")

    subparser.add_argument("--nq", type=int, nargs="+",
            default=[0, 0, 0],
            help="set value of nq1 nq2 nq3.")

    subparser.add_argument("--epsil", type=str, default=None,
            choices=[".true.", ".false."],
            help="set epsil in inputph")

    subparser.add_argument("--lraman", type=str, default=None,
            choices=["true", "false"],
            help="set lraman, can be 'true' or 'false' only. default is None which means 'false' in real world.")

    # Phonopy
    # ---------------------------------------------------------
    subparser.add_argument("--supercell-n", type=int, nargs="+",
            default=[1, 1, 1],
            help="supercell build for Phonopy.")



    # -----------------------------------------------------------------
    #                      run params
    # -----------------------------------------------------------------

    subparser.add_argument("--mpi", type=str, default="",
            help="MPI command: like 'mpirun -np 4'")

    subparser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")

    subparser.add_argument("--jobname", type=str, default="matflow-job",
            help="jobname on the pbs server")

    subparser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")

    subparser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")



    # --------------------------------------------------------------------------
    # SIESTA
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("siesta", help="using siesta as calculator")

    subparser.add_argument("-r", "--runtype", type=int, default=0,
            choices=[0, 1, 2, 3, 4, 5],
            help="choices of runtype. 0->static_run; 1->optimization; 2->cubic-cell; 3->hexagonal-cell; 4->tetragonal-cell; 5->phonpy")

    subparser.add_argument("-d", "--directory", type=str, default="matflow-running",
            help="Directory for the running.")

    # structure file: either xyz or cif. they are exclusive
    # actually this can be put in the main subparser, but it will make the command not like git sub-cmmand
    # so we put them in every subsubparser
    structfile = subparser.add_mutually_exclusive_group(required=True) # at leaset one of cif and xyz is provided
    # argparse will make sure only one of argument in structfile(xyz, cif) appear on command line
    structfile.add_argument("--xyz", type=str, default=None,
            help="The xyz structure file with second line specifying cell parameters")

    structfile.add_argument("--cif", type=str, default=None,
            help="The cif structure file")

    # run option
    subparser.add_argument("--runopt", type=str, default="gen",
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    subparser.add_argument("--auto", type=int, default=3,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")


    # --------------------------------------------------------------------------
    subparser.add_argument("--meshcutoff", type=int, default=200,
            help="MeshCutoff (Ry)")

    subparser.add_argument("--solution-method", type=str, default="diagon",
            choices=["diagon", "OMM", "OrderN", "PEXSI"],
            help="SolutionMethod(diagon, OMM, OrderN, PEXSI)")

    subparser.add_argument("--functional", type=str, default="GGA",
            help="XC.functional")

    subparser.add_argument("--authors", type=str, default="PBE",
            help="XC.authors")

    subparser.add_argument("--tolerance", type=float, default=1.0e-6,
            help="DM.Tolerance")

    subparser.add_argument("--numberpulay", type=int, default=8,
            help="DM.NumberPulay")

    subparser.add_argument("--mixing", type=float, default=0.1,
            help="DM.MixingWeight")

    subparser.add_argument("--kpoints-mp", type=int, nargs="+",
            default=[3, 3, 3],
            help="set kpoints like '3 3 3'")

    subparser.add_argument("--kpath-manual", type=str, nargs="+", default=None,
            help="manual input kpath for band structure calculation")

    subparser.add_argument("--kpath-file", type=str,
            help="file to read the kpath for band structure calculation")

    subparser.add_argument("--occupation", type=str, default="FD",
            choices=["FD", "MP"],
            help="OccupationFunction(FD or MP)")

    subparser.add_argument("--electronic-temperature", type=int, default=300,
            help="Electronic Temperature")


    # ------------------------------
    # properties related parameter
    # ------------------------------
    subparser.add_argument("-p", "--properties" ,nargs="+", type=int, default=[],
            help="Option for properties calculation")

    subparser.add_argument("--pdos-block", type=float, nargs="+",
            default=[-20, 10, 0.2, 500])
    #------------------------------------------------------------------------------------------------
    subparser.add_argument("--kpath", type=str, nargs="+", default=None,
            help="manual input kpath in bandlines modes, like --kpath '0.000000 0.000000 0.000000 GAMMA 5' '0.500000 0.000000 0.000000 X 5' '0.0000 0.000 0.50000 A |' '0.5 0.5 0.5 R '")

    subparser.add_argument("--kpath-manual-file", type=str,
            help="manual input kpath in bandline mode  read from the file")
    #------------------------------------------------------------------------------------------------
    subparser.add_argument("--polarization-grids", nargs="+", type=str,
            default=["10 3 3 no", "2 20 2 no", "4 4 15 no"],
            help="PolarizationGrids")

    subparser.add_argument("--external-electric-field", nargs="+", type=float,
            default=[0.0, 0.0, 0.5],
            help="External Electric field")

    subparser.add_argument("--optical-energy-minimum", type=float,
            default=0.0,
            help="Optical.Energy.Minimum")

    subparser.add_argument("--optical-energy-maximum", type=float,
            default=10.0,
            help="Optical.Energy.Maximum")

    subparser.add_argument("--optical-broaden", type=float,
            default=0.0,
            help="Optical.Broaden")

    subparser.add_argument("--optical-scissor", type=float,
            default=0.0,
            help="Optical.Scissor")

    subparser.add_argument("--optical-mesh", nargs="+", type=int,
            default=[5, 5, 5],
            help="Optical.Mesh")

    subparser.add_argument("--optical-polarization-type", type=str,
            default="unpolarized",
            help="Optical.PolarizationType")

    subparser.add_argument("--optical-vector", nargs="+", type=float,
            default=[1.0, 0.0, 0.5],
            help="Optical.Vector")

    subparser.add_argument("--wannier90-unkgrid", nargs="+", type=int,
            default=[10, 10, 10],
            help="Siesta2Wannier90.UnkGrid[1-3]")

    #           ions relaed parameter
    # ==================================================
    subparser.add_argument("--vc", type=str, default="false",
            choices=["true", "false"],
            help="MD.VariableCell")

    subparser.add_argument("--forcetol", type=float, default=0.04,
            help="Force tolerance in coordinate optimization. default=0.04 eV/Ang")

    subparser.add_argument("--stresstol", type=float, default=1,
            help="Stress tolerance in variable-cell CG optimization. default=1 GPa")

    subparser.add_argument("--targetpressure", type=float, default=0,
            help="Target pressure for Parrinello-Rahman method, variable cell optimizations, and annealing options.")

    # na nc stepa stepc
    # --------------------------------------------------------------------------
    subparser.add_argument("--na", type=int, default=10,
            help="number of a used")
    subparser.add_argument("--nc", type=int, default=10,
            help="number of c used")
    subparser.add_argument("--stepa", type=float, default=0.05,
            help="a step")
    subparser.add_argument("--stepc", type=float, default=0.05,
            help="c step")



    #      Phonopy
    # -------------------------------
    subparser.add_argument("-n", "--supercell-n", type=int, nargs="+",
            default=[1, 1,1],
            help="supercell option for phonopy, like '2 2 2'")


    # -----------------------------------------------------------------
    #                      run params
    # -----------------------------------------------------------------

    subparser.add_argument("--mpi", type=str, default="",
            help="MPI command: like 'mpirun -np 4'")

    subparser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh"],
            help="type of remote server, can be pbs or yh")

    subparser.add_argument("--jobname", type=str, default="matflow-job",
            help="jobname on the pbs server")

    subparser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")

    subparser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")



    # --------------------------------------------------------------------------
    # VASP
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("vasp", help="using vasp as calculator")

    subparser.add_argument("-r", "--runtype", type=int, default=0,
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            help="choices of runtype. 0->static_run; 1->optimization; 2->cubic-cell; 3->hexagonal-cell; 4->tetragonal-cell; 5->neb; 6->vasp-phonon; 7->phonopy")

    subparser.add_argument("-d", "--directory", type=str, default="matflow-running",
            help="Directory for the running.")

    # structure file: either xyz or cif. they are exclusive
    # actually this can be put in the main subparser, but it will make the command not like git sub-cmmand
    # so we put them in every subsubparser
    structfile = subparser.add_mutually_exclusive_group(required=True) # at leaset one of cif and xyz is provided
    # argparse will make sure only one of argument in structfile(xyz, cif) appear on command line
    structfile.add_argument("--xyz", type=str, default=None,
            help="The xyz structure file with second line specifying cell parameters")

    structfile.add_argument("--cif", type=str, default=None,
            help="The cif structure file")

    # run option
    subparser.add_argument("--runopt", type=str, default="gen",
            choices=["gen", "run", "genrun"],
            help="Generate or run or both at the same time.")

    subparser.add_argument("--auto", type=int, default=3,
            choices=[0, 1, 2, 3],
            help="auto:0 nothing, 1: copying files to server, 2: copying and executing, 3: pymatflow run inserver with direct submit,  in order use auto=1, 2, you must make sure there is a working ~/.pymatflow/server_[pbs|yh].conf")

    # --------------------------------------------------------
    #                   INCAR PARAMETERS
    # --------------------------------------------------------
    subparser.add_argument("--prec", type=str, default="Normal",
            choices=["Normal", "Accurate", "A", "N"],
            help="PREC, default value: Normal")

    subparser.add_argument("--encut", type=int, default=300,
            help="ENCUT, default value: 300 eV")

    subparser.add_argument("--ediff", type=float, default=1.0e-4,
            help="EDIFF, default value: 1.0e-4")

    subparser.add_argument("--kpoints-mp", type=int, nargs="+",
            default=[1, 1, 1, 0, 0, 0],
            help="set kpoints like -k 1 1 1 0 0 0")

    subparser.add_argument("--kpoints-mp-scf", type=int, nargs="+",
            default=[1, 1, 1, 0, 0, 0],
            help="set kpoints like -k 1 1 1 0 0 0")

    subparser.add_argument("--kpoints-mp-nscf", type=int, nargs="+",
            default=[3, 3, 3, 0, 0, 0],
            help="set kpoints like -k 1 1 1 0 0 0")

    subparser.add_argument("--kpath-manual", type=str, nargs="+", default=None,
            help="set kpoints for band structure calculation manually")

    subparser.add_argument("--kpath-file", type=str, default="kpath.txt",
            help="set kpoints for band structure calculation manually from file")

    subparser.add_argument("--kpath-intersections", type=int, default=15,
            help="intersection of the line mode kpoint for band calculation")

    subparser.add_argument("--ismear", type=int, default=0,
            help="smearing type(methfessel-paxton(>0), gaussian(0), fermi-dirac(-1), tetra(-4), tetra-bloch-dorrected(-5)), default: 0")

    subparser.add_argument("--sigma", type=float, default=0.01,
            help="determines the width of the smearing in eV.")

    subparser.add_argument("--ivdw", type=int, default=None,
            choices=[0, 11, 12, 21, 202, 4],
            help="IVDW = 0(no correction), 1(dft-d2), 11(dft-d3 Grimme), 12(dft-d3 Becke-Jonson), default: None which means 0, no correction")
    # -----------------------------------------------------------------

    subparser.add_argument("--lorbit", type=int, default=None,
            choices=[0, 1, 2, 5, 10, 11, 12],
            help="together with an appropriate RWIGS, determines whether the PROCAR or PROOUT files are written")

    subparser.add_argument("--loptics", type=str, default="FALSE",
            choices=["TRUE", "FALSE"],
            help="calculates the frequency dependent dielectric matrix after the electronic ground state has been determined.")

    # magnetic related
    subparser.add_argument("--ispin", type=int, default=None,
            choices=[1, 2],
            help="specifies spin polarization: 1->no spin polarized, 2->spin polarized(collinear). combine SIPIN with MAGMOM to study collinear magnetism.")

    subparser.add_argument("--magmom", type=float, nargs="+", default=None,
            help="Specifies the initial magnetic moment for each atom, if and only if ICHARG=2, or if ICHARG=1 and the CHGCAR file contains no magnetisation density.")

    subparser.add_argument("--lnoncollinear", type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE."],
            help="specifies whether fully non-collinear magnetic calculations are performed")

    subparser.add_argument("--lsorbit", type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE."],
            help="specifies whether spin-orbit coupling is taken into account.")

    # hybrid functional
    subparser.add_argument("--lhfcalc", type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE."],
            help=" specifies whether Hartree-Fock/DFT hybrid functional type calculations are performed")

    subparser.add_argument("--hfscreen", type=float, default=None,
            choices=[0.3, 0.2],
            help=" specifies the range-separation parameter in range separated hybrid functionals: HSE03->0.3, HSE06->0.2, must also set LHFCALC=.TRUE.")

    subparser.add_argument("--lsubrot", type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE."],
            help="This flag can be set for hybrid functionals (HF-type calculations).")

    subparser.add_argument("--nsw", type=int, default=1,
            choices=[1],
            help="NSW sets the maximum number of ionic steps")

    subparser.add_argument("--ediffg", type=float, default=None,
            help="EDIFFG, default value: 10*EDIFF")


    subparser.add_argument("--ibrion", type=int, default=2,
            choices=[5, 6, 7, 8],
            help="IBRION = 5(), 6(), 7(), 8(): refer to https://cms.mpi.univie.ac.at/wiki/index.php/IBRION for how to set the algorithm of optimization you need!")



    parser.add_argument("--isif", type=int, default=None,
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            help="ISIF = 0-7: refer to https://cms.mpi.univie.ac.at/wiki/index.php/ISIF for how to set the type of Geometri Optimization you need!")

    subparser.add_argument("--potim", type=float, default=None,
            help="step width scaling (ionic relaxations), default: None = 0.015 in phonon calculation")

    # special
    subparser.add_argument("--algo", type=str, default=None,
            choices=["N", "D", "V", "F"],  #"Exact", "G0W0", "GW0", "GW"],
            help=" a convenient option to specify the electronic minimisation algorithm (as of VASP.4.5) and/or to select the type of GW calculations")

    subparser.add_argument("--ialgo", type=int, default=None,
            choices=[5, 6, 7, 8, 38, 44, 46, 48],
            help="IALGO selects the algorithm used to optimize the orbitals.Mind: We strongly urge the users to select the algorithms via ALGO. Algorithms other than those available via ALGO are subject to instabilities.")

    subparser.add_argument("--addgrid", type=str, default=None,
            choices=[".TRUE.", ".FALSE.", "T", "F"],
            help="ADDGRID determines whether an additional support grid is used for the evaluation of the augmentation charges.")

    subparser.add_argument("--isym", type=int, default=None,
            choices=[-1, 0, 1, 2, 3],
            help=" ISYM determines the way VASP treats symmetry.")

    subparser.add_argument('--lreal', type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE.", "O", "On", "A", "Auto"],
            help="LREAL determines whether the projection operators are evaluated in real-space or in reciprocal space.")

    # write PARAMETERS
    subparser.add_argument("--lwave", type=str, default=None,
            choices=['T', 'F', ".TRUE.", '.FALSE.'],
            help="LWAVE determines whether the wavefunctions are written to the WAVECAR file at the end of a run.")

    subparser.add_argument("--lcharg", type=str, default=None,
            choices=['T', 'F', ".TRUE.", '.FALSE.'],
            help="LCHARG determines whether the charge densities (files CHGCAR and CHG) are written.")


    # properties parameters
    subparser.add_argument("--lelf", type=str, default=None,
            choices=["T", "F", ".TRUE.", ".FALSE."],
            help="LELF determines whether to create an ELFCAR file or not.")



    subparser.add_argument("--nimage", type=int, default=5,
            help="number of image to interpolate. total image will be nimage+2.")

    subparser.add_argument("--images", type=str, nargs="+",
            help="the image xyz file(--images first.xyz final.xyz)")


    # PHONOPY parameters
    # ----------------------------------------
    subparser.add_argument("--supercell-n", type=int, nargs="+",
            default=[1, 1, 1],
            help="supercell for phonopy, like [2, 2, 2]")


    # na stepa nc stepc
    # ----------------------------------------------
    subparser.add_argument("--na", type=int, default=10,
            help="number of a to run")
    subparser.add_argument("--stepa", type=float, default=0.05,
            help="step of a in unit of Angstrom")
    subparser.add_argument("--nc", type=int, default=10,
            help="number of c to run")
    subparser.add_argument("--stepc", type=float, default=0.05,
            help="step of c in unit of Angstrom")


    # pymatflow.vasp inside PARAMETERS
    subparser.add_argument("--selective-dynamics", type=str, default="False",
            choices=["True", "False", "T", "F"],
            help="whether use selective dyanmics")

    # -----------------------------------------------------------------
    #                      run params
    # -----------------------------------------------------------------

    subparser.add_argument("--mpi", type=str, default="",
            help="MPI command")

    subparser.add_argument("--server", type=str, default="pbs",
            choices=["pbs", "yh", "lsf_sz"],
            help="type of remote server, can be pbs or yh or lsf_sz")

    subparser.add_argument("--jobname", type=str, default="vasp-scf",
            help="jobname on the pbs server")

    subparser.add_argument("--nodes", type=int, default=1,
            help="Nodes used in server")

    subparser.add_argument("--ppn", type=int, default=32,
            help="ppn of the server")



    # ==========================================================
    # transfer parameters from the arg subparser to static_run setting
    # ==========================================================

    args = parser.parse_args()

    # if no argument passed to matflow
    if len(sys.argv) == 1:
        # display help message when no args provided
        parser.print_help()
        sys.exit(1)

    # dealing wich structure files
    if args.xyz != None:
        xyzfile = args.xyz
    else:
        os.system("cif-to-xyz-modified.py -i %s -o %s.xyz" % (args.cif, args.cif))
        xyzfile = "%s.xyz" % args.cif




    if args.driver == "abinit":
        params = {}
        kpoints = {}

        params["chkprim"] = args.chkprim
        params["ecut"] = args.ecut
        params["ixc"] = args.ixc
        params["vdw_xc"] = args.vdw_xc
        params["vdw_tol"] = args.vdw_tol

        kpoints["kptopt"] = args.kptopt
        kpoints["ngkpt"] = args.ngkpt

        params["occopt"] = args.occopt
        params["nband"] = args.nband
        params["occ"] = args.occ


        if args.runtype == 0:
            # static
            params["nsppol"] = args.nsppol
            params["prtden"] = args.prtden
            params["prtdos"] = args.prtdos
            from pymatflow.abinit.static import static_run
            task = static_run()
            if get_kpath(args.kpath_manual, args.kpath_file) == None:
                print("================================================\n")
                print("Warning: matflow abinit\n")
                print("in abinit static runing you must provide kpath\n")
                sys.exit(1)
            task.dataset[3].electrons.kpoints.set_band(kptbounds=get_kpath(args.kpath_manual, args.kpath_file))
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 1:
            # optimization
            params["optcell"] = args.optcell
            params["chkdilatmx"] = args.chkdilatmx
            params["dilatmx"] = args.dilatmx
            params["ionmov"] = args.ionmov
            params["ecutsm"] = args.ecutsm
            from pymatflow.abinit.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 2:
            ## cubic optimization
            params["optcell"] = 0 # must be 0
            params["ionmov"] = args.ionmov
            from pymatflow.abinit.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cubic(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa)
        elif args.runtype == 3:
            # hexagonal optimization
            params["optcell"] = 0 # must be 0
            params["ionmov"] = args.ionmov
            from pymatflow.abinit.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.hexagonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa, nc=args.nc, stepc=args.stepc)
        elif args.runtype == 4:
            # tetragonal optimization
            params["optcell"] = 0 # must be 0
            params["ionmov"] = args.ionmov
            from pymatflow.abinit.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.tetragonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa, nc=args.nc, stepc=args.stepc)
        elif args.runtype == 5:
            # dfpt-elastic-piezo-dielec
            from pymatflow.abinit.dfpt import dfpt_elastic_piezo_dielec
            task = dfpt_elastic_piezo_dielec()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 6:
            # dfpt-phonon
            from pymatflow.abinit.dfpt import dfpt_phonon
            task = dfpt_phonon()
            task.get_qpath(get_kpath(args.kpath_manual, args.kpath_file))

            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.set_properties(properties=args.properties)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 7:
            # phonopy phonon
            from pymatflow.abinit.phonopy import phonopy_run
            task = phonopy_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints=kpoints)
            task.supercell_n = args.supercell_n
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonopy(directory=args.directory, runopt=args.runopt, auto=args.auto)
        else:
            pass
# ==============================================================================
# CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K CP2K C2PK CP2K
# ==============================================================================
    elif args.driver == "cp2k":
        params = {}

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
        params["FORCE_EVAL-DFT-XC-VDW_POTENTIAL-POTENTIAL_TYPE"] = args.vdw_potential_type
        params["FORCE_EVAL-DFT-XC-VDW_POTENTIAL-PAIR_POTENTIAL-TYPE"] = args.pair_type
        params["FORCE_EVAL-DFT-XC-VDW_POTENTIAL-PAIR_POTENTIAL-R_CUTOFF"] = args.r_cutoff
        params["FORCE_EVAL-DFT-PRINT-ELF_CUBE-STRIDE"] = args.dft_print_elf_cube_stride
        params["FORCE_EVAL-DFT-PRINT-E_DENSITY_CUBE-STRIDE"] = args.dft_print_e_density_cube_stride
        params["FORCE_EVAL-PROPERTIES-RESP-SLAB_SAMPLING-RANGE"] = args.properties_resp_slab_sampling_range
        params["FORCE_EVAL-PROPERTIES-RESP-SLAB_SAMPLING-SURF_DIRECTION"] = args.properties_resp_slab_sampling_surf_direction
        params["FORCE_EVAL-PROPERTIES-RESP-SLAB_SAMPLING-ATOM_LIST"] = args.properties_resp_slab_sampling_atom_list
        if args.runtype == 0:
            from pymatflow.cp2k.static import static_run
            task = static_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_printout(option=args.printout_option)
            if 2 in args.printout_option and kpath != None:
                task.force_eval.dft.printout.band_structure.set_band(kpath=get_kpath(args.kpath_manual, args.kpath_file))
            task.set_vdw(usevdw=True if args.usevdw.lower() == "true" else False)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.scf(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 1:
            # geo opt
            params["MOTION-GEO_OPT-MAX_ITER"] = args.geo_opt_max_iter
            params["MOTION-GEO_OPT-OPTIMIZER"] = args.geo_opt_optimizer
            params["MOTION-GEO_OPT-TYPE"] = args.geo_opt_type
            params["MOTION-GEO_OPT-MAX_DR"] = args.geo_opt_max_dr
            params["MOTION-GEO_OPT-MAX_FORCE"] = args.geo_opt_max_force
            params["MOTION-GEO_OPT-RMS_DR"] = args.geo_opt_rms_dr
            params["MOTION-GEO_OPT-RMS_FORCE"] = args.geo_opt_rms_force
            from pymatflow.cp2k.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_geo_opt()
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.geo_opt(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 2:
            # cell opt
            params["MOTION-CELL_OPT-MAX_ITER"] = args.cell_opt_max_iter
            params["MOTION-CELL_OPT-OPTIMIZER"] = args.cell_opt_optimizer
            params["MOTION-CELL_OPT-TYPE"] = args.cell_opt_type
            params["MOTION-CELL_OPT-MAX_DR"] = args.cell_opt_max_dr
            params["MOTION-CELL_OPT-MAX_FORCE"] = args.cell_opt_max_force
            params["MOTION-CELL_OPT-RMS_DR"] = args.cell_opt_rms_dr
            params["MOTION-CELL_OPT-RMS_FORCE"] = args.cell_opt_rms_force
            params["MOTION-CELL_OPT-PRESSURE_TOLERANCE"] = args.cell_opt_pressure_tolerance
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_cell_opt()
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cell_opt(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 3:
            # cubic cell opt
            params["MOTION-GEO_OPT-MAX_ITER"] = args.geo_opt_max_iter
            params["MOTION-GEO_OPT-OPTIMIZER"] = args.geo_opt_optimizer
            params["MOTION-GEO_OPT-TYPE"] = args.geo_opt_type
            params["MOTION-GEO_OPT-MAX_DR"] = args.geo_opt_max_dr
            params["MOTION-GEO_OPT-MAX_FORCE"] = args.geo_opt_max_force
            params["MOTION-GEO_OPT-RMS_DR"] = args.geo_opt_rms_dr
            params["MOTION-GEO_OPT-RMS_FORCE"] = args.geo_opt_rms_force
            from pymatflow.cp2k.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_geo_opt()
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cubic(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.nc, stepa=args.stepa)
        elif args.runtype == 4:
            # hexagonal cell opt
            params["MOTION-GEO_OPT-MAX_ITER"] = args.geo_opt_max_iter
            params["MOTION-GEO_OPT-OPTIMIZER"] = args.geo_opt_optimizer
            params["MOTION-GEO_OPT-TYPE"] = args.geo_opt_type
            params["MOTION-GEO_OPT-MAX_DR"] = args.geo_opt_max_dr
            params["MOTION-GEO_OPT-MAX_FORCE"] = args.geo_opt_max_force
            params["MOTION-GEO_OPT-RMS_DR"] = args.geo_opt_rms_dr
            params["MOTION-GEO_OPT-RMS_FORCE"] = args.geo_opt_rms_force
            from pymatflow.cp2k.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_geo_opt()
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.hexagonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 5:
            # tetragonal cell opt
            params["MOTION-GEO_OPT-MAX_ITER"] = args.geo_opt_max_iter
            params["MOTION-GEO_OPT-OPTIMIZER"] = args.geo_opt_optimizer
            params["MOTION-GEO_OPT-TYPE"] = args.geo_opt_type
            params["MOTION-GEO_OPT-MAX_DR"] = args.geo_opt_max_dr
            params["MOTION-GEO_OPT-MAX_FORCE"] = args.geo_opt_max_force
            params["MOTION-GEO_OPT-RMS_DR"] = args.geo_opt_rms_dr
            params["MOTION-GEO_OPT-RMS_FORCE"] = args.geo_opt_rms_force
            from pymatflow.cp2k.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_geo_opt()
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.tetragonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 6:
            # phonopy
            from pymatflow.cp2k.phonopy import phonopy_run
            task = phonopy_run()
            task.get_xyz(xyzfile)
            task.supercell_n = args.supercell_n
            task.set_params(params=params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonopy(directory=args.directory, runopt=args.runopt, auto=args.auto)
        else:
            pass
# ==============================================================================
# Quantum ESPERSSO Quantum ESPERSSO Quantum ESPERSSO Quantum ESPERSSO Quantum ESPERSSO
# ==============================================================================
    elif args.driver == "qe":
        control = {}
        electrons = {}
        system = {}
        ions = {}

        control["tstress"] = args.tstress
        system["ecutwfc"] = args.ecutwfc
        system["ecutrho"] = args.ecutrho
        system["occupations"] = args.occupations
        system["smearing"] = args.smearing
        system["degauss"] = args.degauss
        system["vdw_corr"] = args.vdw_corr
        system["nbnd"] = args.nbnd
        electrons["conv_thr"] = args.conv_thr

        system["nspin"] = args.nspin
        system["starting_magnetization"] = args.starting_magnetization
        system["noncolin"] = args.noncolin

        path = {}
        path["string_method"] = args.string_method
        path["nstep_path"] = args.nstep_path
        path["opt_scheme"] = args.opt_scheme
        path["num_of_images"] = args.num_of_images
        path["k_max"] = args.k_max
        path["k_min"] = args.k_min
        path["CI_scheme"] = args.ci_scheme
        path["path_thr"] = args.path_thr
        path["ds"] = args.ds
        path["first_last_opt"] = args.first_last_opt

        # for ph.x
        inputph = {}
        inputph["tr2_ph"] = args.tr2_ph
        inputph["lraman"] = args.lraman
        inputph["epsil"] = args.epsil
        inputph["nq1"] = args.nq[0]
        inputph["nq2"] = args.nq[1]
        inputph["nq3"] = args.nq[2]


        if args.runtype == 0:
            # static scf nscf projwfc bands pp.x in a single run
            from pymatflow.qe.static import static_run
            projwfc_input = {}
            if args.projwfc_ngauss == 'default':
                ngauss = args.projwfc_ngauss
            else:
                ngauss = int(args.projwfc_ngauss)
            if args.projwfc_degauss == 'default':
                degauss = args.projwfc_degauss
            else:
                degauss = float(args.projwfc_degauss)
            if args.projwfc_emin == 'default':
                emin = args.projwfc_emin
            else:
                emin = float(args.projwfc_emin)
            if args.projwfc_emax == 'default':
                emax = args.projwfc_emax
            else:
                emax = float(args.projwfc_emax)
            if args.projwfc_deltae == 'default':
                deltae = args.projwfc_deltae
            else:
                deltae = float(args.projwfc_deltae)

            projwfc_input["filpdos"] = args.projwfc_filpdos
            projwfc_input["ngauss"] = ngauss
            projwfc_input["degauss"] = degauss
            projwfc_input["emin"] = emin
            projwfc_input["emax"] = emax
            projwfc_input["deltae"] = deltae
            bands = {}
            bands["lsym"] = args.lsym
            inputpp = {}
            plotpp = {}
            inputpp["plot_num"] = args.plot_num
            plotpp["iflag"] = args.iflag
            plotpp["output_format"] = args.output_format
            task = static_run()
            task.get_xyz(xyzfile)
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons)
            task.set_atomic_forces(pressure=args.pressure, pressuredir=args.pressuredir)
            task.set_projwfc(projwfc_input=projwfc_input)
            task.set_bands(bands_input=bands)
            task.set_pp(inputpp=inputpp, plotpp=plotpp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto, kpath=get_kpath(args.kpath_manual, args.kpath_file))
        elif args.runtype == 1:
            # relax
            from pymatflow.qe.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_relax()
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons, ions=ions)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.relax(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 2:
            # vc-relax
            from pymatflow.qe.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_vc_relax()
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons, ions=ions)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.vc_relax(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 3:
            # cubic cell opt
            from pymatflow.qe.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_relax()
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons, ions=ions)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cubic(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa)
        elif args.runtype == 4:
            # hexagonal cell opt
            from pymatflow.qe.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_relax()
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons, ions=ions)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.hexagonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 5:
            # tetragonal cell opt
            from pymatflow.qe.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_relax()
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons, ions=ions)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.tetragonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 6:
            from pymatflow.qe.neb import neb_run
            task = neb_run()
            task.get_images(images=args.images)
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_path(path=path)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.neb(directory=directory, runopt=args.runopt, restart_mode=args.restart_mode, auto=args.auto)
        elif args.runtype == 7:
            from pymatflow.qe.dfpt import dfpt_run
            task = dfpt_run()
            task.get_xyz(xyzfile)
            task.set_inputph(inputph=inputph)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phx(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 8:
            # phonopy
            from pymatflow.qe.phonopy import phonopy_run
            task = phonopy_run()
            task.get_xyz(xyzfile)
            task.set_kpoints(kpoints_option=args.kpoints_option, kpoints_mp=args.kpoints_mp)
            task.set_params(control=control, system=system, electrons=electrons)
            task.supercell_n = args.supercell_n
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonopy(directory=args.directory, runopt=args.runopt, auto=args.auto)
        else:
            pass

# ==============================================================================
# SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA SIESTA
# ==============================================================================
    elif args.driver == "siesta":
        params = {}

        params["MeshCutoff"] = args.meshcutoff
        params["SolutionMethod"] = args.solution_method
        params["XC.funtional"] = args.functional
        params["XC.authors"] = args.authors
        params["DM.Tolerance"] = args.tolerance
        params["DM.NumberPulay"] = args.numberpulay
        params["DM.MixingWeight"] = args.mixing
        params["OccupationFunction"] = args.occupation
        params["ElectronicTemperature"] = args.electronic_temperature

        if args.runtype == 0:
            # static
            from pymatflow.siesta.static import static_run
            task = static_run()
            task.get_xyz(xyzfile)

            task.properties.set_params(
                #bandlines = args.bandlines,
                #bandpoints = args.bandpoints,
                polarization_grids = args.polarization_grids,
                external_electric_field = args.external_electric_field,
                optical_energy_minimum = args.optical_energy_minimum,
                optical_energy_maximum = args.optical_energy_maximum,
                optical_broaden = args.optical_broaden,
                optical_scissor = args.optical_scissor,
                optical_mesh = args.optical_mesh,
                optical_polarization_type = args.optical_polarization_type,
                optical_vector = args.optical_vector,
                wannier90_unkgrid = args.wannier90_unkgrid,
                )

            if 3 in args.properties:
                task.properties.bandlines = bandlines

            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.scf(directory=args.directory, runopt=args.runopt, auto=args.auto, properties=args.properties)
        elif args.runtype == 1:
            # optimization
            from pymatflow.siesta.opt import opt_run
            params["MD.VariableCell"] = args.vc
            params["MD.MaxForceTol"] = args.forcetol
            params["MD.MaxStressTol"] = args.stresstol
            params["MD.TargetPressure"] = args.targetpressure
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.opt(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 2:
            # cubic cell
            from pymatflow.siesta.opt import opt_run
            params["MD.VariableCell"] = "false"
            params["MD.MaxForceTol"] = args.forcetol
            params["MD.MaxStressTol"] = args.stresstol
            params["MD.TargetPressure"] = args.targetpressure
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cubic(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa)
        elif args.runtype == 3:
            # hexagonal cell
            from pymatflow.siesta.opt import opt_run
            params["MD.VariableCell"] = "false"
            params["MD.MaxForceTol"] = args.forcetol
            params["MD.MaxStressTol"] = args.stresstol
            params["MD.TargetPressure"] = args.targetpressure
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.hexagonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 4:
            # tetragonal cell
            from pymatflow.siesta.opt import opt_run
            params["MD.VariableCell"] = "false"
            params["MD.MaxForceTol"] = args.forcetol
            params["MD.MaxStressTol"] = args.stresstol
            params["MD.TargetPressure"] = args.targetpressure
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.tetragonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 5:
            # phonopy
            from pymatflow.siesta.phonopy import phonopy_run
            task = phonopy_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.supercell_n = args.supercell_n
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonopy(directory=args.directory, runopt=args.runopt, auto=args.auto)
        else:
            pass
    elif args.driver == "vasp":
        params = {}
        params["PREC"] = args.prec
        params["ENCUT"] = args.encut
        params["EDIFF"] = args.ediff
        params["ISMEAR"] = args.ismear
        params["SIGMA"] = args.sigma
        params["IVDW"] = args.ivdw
        params["EDIFFG"] = args.ediffg
        params["NSW"] = args.nsw
        params["IBRION"] = args.ibrion
        params["ISIF"] = args.isif
        params["POTIM"] = args.potim

        params["LORBIT"] = args.lorbit
        params["LOPTICS"] = args.loptics
        params["LSUBROT"] = args.lsubrot

        params["ALGO"] = args.algo
        params["IALGO"] = args.ialgo
        params["ADDGRID"] = args.addgrid
        params["ISYM"] = args.isym
        params["LREAL"] = args.lreal
        params["ISPIN"] = args.ispin
        params["MAGMOM"] = args.magmom # magmom can be a list that can be automatically dealt with by base.incar.to_incar()
        params["LNONCOLLLINEAR"] = args.lnoncollinear
        params["LSORBIT"] = args.lsorbit
        params["ALGO"] = args.algo
        params["LHFCALC"] = args.lhfcalc
        params["HFSCREEN"] = args.hfscreen

        params["LELF"] = args.lelf

        if args.runtype == 0:
            # static
            from pymatflow.vasp.static import static_run
            task = static_run()
            task.get_xyz(xyzfile)
            task.set_params(params)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.run(directory=args.directory, runopt=args.runopt, auto=args.auto, kpoints_mp_scf=args.kpoints_mp_scf, kpoints_mp_nscf=args.kpoints_mp_nscf, kpath=get_kpath(args.kpath_manual, args.kpath_file), kpath_intersections=args.kpath_intersections)
        elif args.runtype == 1:
            # optimization
            from pymatflow.vasp.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.poscar.selective_dynamics = True if args.selective_dynamics.upper()[0] == "T" else False
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.optimize(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 2:
            # cubic cell
            from pymatflow.vasp.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.cubic(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, stepa=args.stepa)
        elif args.runtype == 3:
            # hexagonal cell
            from pymatflow.vasp.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.hexagonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 4:
            # tetragonal cell
            from pymatflow.vasp.opt import opt_run
            task = opt_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.tetragonal(directory=args.directory, runopt=args.runopt, auto=args.auto, na=args.na, nc=args.nc, stepa=args.stepa, stepc=args.stepc)
        elif args.runtype == 5:
            # neb
            from pymatflow.vasp.neb import neb_run
            task = neb_run()
            task.get_images(args.images)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.nimage = args.nimage
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.neb(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 6:
            # vasp phonon
            from pymatflow.vasp.phonon import phonon_run
            task = phonon_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.supercell_n = args.supercell_n
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonon(directory=args.directory, runopt=args.runopt, auto=args.auto)
        elif args.runtype == 7:
            # phonopy
            from pymatflow.vasp.phonopy import phonopy_run
            task = phonopy_run()
            task.get_xyz(xyzfile)
            task.set_params(params=params)
            task.set_kpoints(kpoints_mp=args.kpoints_mp)
            task.supercell_n = args.supercell_n
            task.set_run(mpi=args.mpi, server=args.server, jobname=args.jobname, nodes=args.nodes, ppn=args.ppn)
            task.phonopy(directory=args.directory, runopt=args.runopt, auto=args.auto)
    # --------------------------------------------------------------------------



if __name__ == "__main__":
    main()
