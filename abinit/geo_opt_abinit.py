#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg


"""
Usage:
    python geo_opt_abinit.py xxx.xyz
    xxx.xyz is the input structure file

    make sure the xyz structure file and the pseudopotential file
    for all the elements of the system is in the directory.
"""


class Atom:
    """
    a representation of atom with xyz coordinates
    """
    def __init__(self, name=None, x=0, y=0, z=0):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    def set_name(self, name):
        self.name = name
    def set_x(self, x):
        self.x = float(x)
    def set_y(self, y):
        self.y = float(y)
    def set_z(self, z):
        self.z = float(z)


class XYZ:
    """
    a representation of xyz file
    """
    def __init__(self, xyz_f=sys.argv[1]):
        self.file = xyz_f
        self.natom = 0
        self.nspecies = 0
        self.atoms = []
        self.specie_labels = dict()
        self.get_info()
        self.cell = self.get_cell()

    def get_info(self):
        with open(self.file, 'r') as fin:
            self.natom = int(fin.readline())
            fin.readline()
            i = 0
            while i < self.natom:
                line = fin.readline()
                atom = Atom(line.split()[0], float(line.split()[1]), float(line.split()[2]), float(line.split()[3]))
                self.atoms.append(atom)
                i += 1
        self.set_species_number()

    def set_species_number(self):
        names = [self.atoms[x].name for x in range(self.natom)]
        species = set(names)
        species = list(species)
        species_with_order = {}
        for i in species:
            species_with_order[i] = mg.Element(i).number
        tmp = sorted(zip(species_with_order.values(), species_with_order.keys()))
        for i in range(len(tmp)):
            tmp[i] = list(tmp[i])
        for i in range(len(tmp)):
            tmp[i][0] = i + 1
        tmp = dict(tmp)
        self.specie_labels = dict(zip(tmp.values(), tmp.keys()))
        self.nspecies = len(self.specie_labels)

    def to_abinit(self, fname):
        cell = self.cell
        with open(fname, 'a') as fout:
            fout.write("acell 1 1 1\n") # scaling with 1 means no actually scaling of rprim by acell
            fout.write("rprim\n")
            fout.write("%f %f %f\n" % (cell[0], cell[1], cell[2]))
            fout.write("%f %f %f\n" % (cell[3], cell[4], cell[5]))
            fout.write("%f %f %f\n" % (cell[6], cell[7], cell[8]))

            fout.write("ntypat %d\n" % self.nspecies)
            fout.write("natom %d\n" % self.natom)
            fout.write("typat ")
            for atom in self.atoms:
                fout.write("%d " % self.specie_labels[atom.name])
            fout.write("\n")
            fout.write("znucl ")
            for element in xyz.specie_labels:
                fout.write(str(mg.Element[element].number))
                fout.write(" ")
            fout.write("\n")
            fout.write("\n")
            fout.write("xangst\n")
            for atom in self.atoms:
                fout.write("%f %f %f\n" % (atom.x, atom.y, atom.z))
            fout.write("\n")

    def get_cell(self):
        """
        cell defined in xxx.xyz must be in format like this:
        cell: 4.08376 0.00000 0.00000 | 0.00000 4.00251 0.00000 | -0.05485 0.00000 8.16247
        """
        with open(self.file, 'r') as fin:
            fin.readline()
            line = fin.readline()
        return [float(line.split()[i]) for i in [1, 2, 3, 5, 6, 7, 9, 10, 11]]

    def update(self, newxyzfile):
        self.file = newxyzfile
        self.natom = 0
        self.nspecies = 0
        self.atoms = []
        self.specie_labels = dict()
        self.get_info()
        self.cell = self.get_cell()

        

# OK now we can use XYZ class to extract information 
# from the xyz file: sys.argv[1]

#ecut_min = int(sys.argv[2]) # in Ry: 1 Ry = 13.6 ev
#ecut_max = int(sys.argv[3])
#ecut_step = int(sys.argv[4])
cutoff = 40

xyz = XYZ()

base_project_name = "geo-opt-calc"
if os.path.exists("./tmp-geo-opt"):
    shutil.rmtree("./tmp-geo-opt")
os.mkdir("./tmp-geo-opt")
os.chdir("./tmp-geo-opt")
#shutil.copyfile("../%s" % sys.argv[1], "%s" % sys.argv[1])
#shutil.copyfile("../Li.psf", "Li.psf")
#shutil.copyfile("../Li.psp8", "Li.psp8")
#shutil.copyfile("../H.psp8", "H.psp8")
os.system("cp ../*.psp8 ./")


inp_name = "geo-opt-calc.in"
files_name = "geo-opt-calc.files"
with open(files_name, 'w') as fout:
    fout.write(inp_name)
    fout.write("\n")
    fout.write("geo-opt-calc.out\n")
    fout.write("geo-opt-calci\n")
    fout.write("geo-opt-calco\n")
    fout.write("temp\n")
    for element in xyz.specie_labels:
        fout.write("%s\n" % (element + ".psp8"))
    #
with open(inp_name, 'w') as fout:
    fout.write("ecut %d\n" % cutoff)
    fout.write("ixc = 11\n")
    fout.write("kptopt 1\n")
    fout.write("ngkpt 1 1 1\n")
    fout.write("occopt 3\n") # fermi dirac smearing of occupation
    fout.write("nstep 100\n")
    fout.write("toldfe 1.0d-6\n")
    fout.write("diemac 2.0\n")
    # geo opt setting
    fout.write("ionmov 3\n")
    fout.write("optcell 0\n")
    fout.write("ntime 100\n")
    fout.write("tolmxde 0.0001 eV\n") # 
    fout.write("tolmxf 0 #5.0d-3  # Ha/Bohr\n") # tolmxde 与tolmxf两者只能设置一个为有效值, 其一需要定义为0
    fout.write("\n")
xyz.to_abinit(inp_name)

# run the simulation
#out_f_name = "geo-opt-calc.out.log"
os.system("abinit < %s" % (files_name))

# analyse the result

import matplotlib.pyplot as plt
# use abiview.py to view information in relaxation
os.system("abiview.py hist %so_HIST.nc" % base_project_name)


