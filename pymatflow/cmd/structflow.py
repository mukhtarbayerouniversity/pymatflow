#!/usr/bin/env python

import os
import sys
import argparse



def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="driver", title="subcommands", description="choose one and only one subcommand")

    # --------------------------------------------------------------------------
    # supercell builder
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("supercell", help="using supercell subcommand")

    subparser.add_argument("-i", "--input", type=str,
            help="input xyz file")

    subparser.add_argument("-o", "--output", type=str,
            help="output xyz file")

    subparser.add_argument("-n", "--supern", nargs="+", type=int,
            help="bulid supern:[int, int, int] supercell")


    # --------------------------------------------------------------------------
    # fix atoms
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("fix", help="using fix subcommand")

    subparser.add_argument("-i", "--input", help="intput xyz file", type=str)
    subparser.add_argument("-o", "--output", help="output xyz file", type=str)
    subparser.add_argument("--fix", help="list of fixed atoms", nargs='+', type=int)


    # --------------------------------------------------------------------------
    # convert file type
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("convert", help="using convert subcommand")

    subparser.add_argument("-i", "--input", type=str,
            help="input structure file")

    subparser.add_argument("-o", "--output", type=str,
            help="output structure file")

    # --------------------------------------------------------------------------
    # kpath
    # --------------------------------------------------------------------------
    subparser = subparsers.add_parser("kpath", help="using kpath subcommand")

    subparser.add_argument("--engine", type=str, default="seekpath",
            choices=["seekpath"],
            help="choose tool to generate kpath")

    subparser.add_argument("-i", "--input", type=str, default=None,
            help="the input xyz structure file")

    subparser.add_argument("-o", "--output", type=str, default="kpath-from-seekpath.txt",
            help="the output kpoints file")




    # ==========================================================
    # transfer parameters from the arg subparser to static_run setting
    # ==========================================================

    args = parser.parse_args()

    # if no argument passed to matflow
    if len(sys.argv) == 1:
        # display help message when no args provided
        parser.print_help()
        sys.exit(1)



    if args.driver == "supercell":
        from pymatflow.base.xyz import base_xyz
        from pymatflow.structure.crystal import crystal
        xyz = base_xyz()
        xyz.get_xyz(args.input)
        structure = crystal()
        new_structure = crystal()
        structure.from_base_xyz(xyz)
        supercell = structure.build_supercell(args.supern)
        new_structure.get_cell_atoms(cell=supercell["cell"], atoms=supercell["atoms"])
        new_structure.to_base_xyz().to_xyz_file(args.output)
    elif args.driver == "fix":
        fix_str = ""
        for i in args.fix:
            fix_str += "%d " % i
        os.system("xyz-fix-atoms.py -i %s -o %s --fix %s" % (args.input, args.output, fix_str))
    elif args.driver == "convert":
        # will convert file type according to the suffix of the specified input and output file
        if args.input.split(".")[-1] == "xyz":
            if args.output.split(".")[-1] == "cif":
                import pymatflow.third.aseio as aseio
                from pymatflow.structure.crystal import crystal
                print("=========================================================\n")
                print("         structflow convert xyz to cif\n")
                print("---------------------------------------------------------\n")
                print("with the help from ase.io\n")
                a = crystal()
                a.from_xyz_file(args.input)
                aseio.write_cif(cell=a.cell, atoms=a.atoms, filepath=args.output)
            elif args.output.split(".")[-1] == "xtd":
                import pymatflow.third.aseio as aseio
                from pymatflow.structure.crystal import crystal
                print("=========================================================\n")
                print("         structflow convert xyz to xtd\n")
                print("---------------------------------------------------------\n")
                print("with the help from ase.io\n")
                a = crystal()
                a.from_xyz_file(args.input)
                aseio.write_xtd(cell=a.cell, atoms=a.atoms, filepath=args.output)
            else:
                pass
        elif args.input.split(".")[-1] == "cif":
            if args.output.split(".")[-1] == "xyz":
                print("=====================================\n")
                print("      structflow convertt cif to xyz\n")
                print("-------------------------------------\n")
                print("convert from cif to xyz-modified\n")
                print("with the help from ase.io\n")
                a = crystal()
                a.cell, a.atoms = aseio.read_cif(args.cif)
                a.write_xyz(filepath=args.xyz)
            elif args.output.split(".")[-1] == "xtd":
                import pymatflow.third.aseio as aseio
                #from pymatflow.structure.crystal import crystal
                print("=========================================================\n")
                print("         structflow convert cif to xtb\n")
                print("---------------------------------------------------------\n")
                print("with the help from ase.io\n")
                cell, atoms = aseio.read_cif(args.input)
                aseio.write_xtd(cell=cell, atoms=atoms, filepath=args.output)
            else:
                pass
        elif args.input.split(".")[-1] == "xtb":
            if args.output.split(".")[-1] == "xyz":
                print("=====================================\n")
                print("      structflow convert xtb to xyz\n")
                print("-------------------------------------\n")
                print("convert from xtb to xyz-modified\n")
                print("with the help from ase.io\n")
                a = crystal()
                a.cell, a.atoms = aseio.read_xtb(args.input)
                a.write_xyz(filepath=args.output)
            elif args.output.split(".")[-1] == "cif":
                print("=====================================\n")
                print("      structflow convert xtb to cif\n")
                print("-------------------------------------\n")
                print("convert from xtb to xyz-modified\n")
                print("with the help from ase.io\n")
                cell, atoms = aseio.read_xtb(args.input)
                aseio.write_cif(cell=cell, atoms=atoms, filepath=args.output)

        else:
            pass
    elif args.driver == "kpath":
        if args.engine == "seekpath":
            os.system("kpath-xyz-seekpath.py -i %s -o %s" % (args.input, args.output))
        else:
            pass
    # --------------------------------------------------------------------------



if __name__ == "__main__":
    main()
