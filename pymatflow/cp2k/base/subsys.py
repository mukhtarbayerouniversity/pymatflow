#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg

from pymatflow.base.xyz import base_xyz

"""
Usage:
"""

class cp2k_subsys_cell:
    def __init__(self):
        self.params = {
                "ALPHA_BETA_GAMMA": None,
                "CELL_FILE_FORMAT": None,
                "CELL_FILE_NAME": None,
                "MULTIPLE_UNIT_CELL": None,
                "PERIODIC": None,
                "SYMMETRY": None,
                }
        self.status = False

    def to_input(self, fout, xyz):
        """
        fout: a file stream for writing
        """
        fout.write("\t\t&CELL\n")
        #fout.write("\t\t\tA %.9f %.9f %.9f\n" % (xyz.cell[0], xyz.cell[1], xyz.cell[2]))
        #fout.write("\t\t\tB %.9f %.9f %.9f\n" % (xyz.cell[3], xyz.cell[4], xyz.cell[5]))
        #fout.write("\t\t\tC %.9f %.9f %.9f\n" % (xyz.cell[6], xyz.cell[7], xyz.cell[8]))
        fout.write("\t\t\tA %.9f %.9f %.9f\n" % (xyz.cell[0][0], xyz.cell[0][1], xyz.cell[0][2]))
        fout.write("\t\t\tB %.9f %.9f %.9f\n" % (xyz.cell[1][0], xyz.cell[1][1], xyz.cell[1][2]))
        fout.write("\t\t\tC %.9f %.9f %.9f\n" % (xyz.cell[2][0], xyz.cell[2][1], xyz.cell[2][2]))
        fout.write("\t\t\tPERIODIC XYZ\n")
        fout.write("\t\t&END CELL\n")


class cp2k_subsys_colvar:
    def __init__(self):
        self.status = False

class cp2k_subsys_coord:
    def __init__(self):
        self.status = False

class cp2k_subsys_core_coord:
    def __init__(self):
        self.status = False

class cp2k_subsys_core_velocity:
    def __init__(self):
        self.status = False

class cp2k_subsys_kind:
    def __init__(self):
        self.status = False

        self.basis_set = dict()
        self.potential = dict()
        for i in mg.Element:
            self.basis_set[str(i)] = 'DZVP-MOLOPT-SR-GTH'
            self.potential[str(i)] = 'GTH-PBE'

    def to_input(self, fout, xyz):
        """
        fout: a file stream for writing
        """
        for element in xyz.specie_labels:
                fout.write("\t\t&KIND %s\n" % element)
                fout.write("\t\t\tBASIS_SET %s\n" % self.basis_set[element])
                fout.write("\t\t\tPOTENTIAL %s\n" % self.potential[element])
                fout.write("\t\t&END KIND\n")

class cp2k_subsys_multipoles:
    def __init__(self):
        self.status = False

class cp2k_subsys_print:
    def __init__(self):
        self.status = False

class cp2k_subsys_rng_init:
    def __init__(self):
        self.status = False

class cp2k_subsys_shell_coord:
    def __init__(self):
        self.status = False

class cp2k_subsys_shell_velocity:
    def __init__(self):
        self.status = False

class cp2k_subsys_topology:
    def __init__(self):
        self.status = False

    def to_input(self, fout, xyz):
        """
        fout: a file stream for writing
        """
        fout.write("\t\t&TOPOLOGY\n")
        fout.write("\t\t\tCOORD_FILE_FORMAT xyz\n")
        fout.write("\t\t\tCOORD_FILE_NAME %s\n" % xyz.file)
        fout.write("\t\t&END TOPOLOGY\n")

class cp2k_subsys_velocity:
    def __init__(self):
        self.status = False




# ===========================
# CP2K / FORCE_EVAL / SUBSYS
# ===========================
class cp2k_subsys:
    """

    """
    def __init__(self):
        #super().__init__()
        self.xyz = base_xyz()
        self.params = {
                "SEED": None,
                }
        self.status = False

        self.cell = cp2k_subsys_cell()

        self.colvar = cp2k_subsys_colvar()

        self.coord = cp2k_subsys_coord()

        self.core_coord = cp2k_subsys_core_coord()

        self.core_velocity = cp2k_subsys_core_velocity()

        self.kind = cp2k_subsys_kind()

        self.multipoles = cp2k_subsys_multipoles()

        self.printout = cp2k_subsys_print()

        self.rng_init = cp2k_subsys_rng_init()

        self.shell_coord = cp2k_subsys_shell_coord()

        self.shell_velocity = cp2k_subsys_shell_velocity()

        self.topology = cp2k_subsys_topology()

        self.velocity = cp2k_subsys_velocity()

        # basic_setting
        self.kind.status = True
        self.cell.status = True
        self.topology.status = True
    
    def to_input(self, fout):
        """
        fout: a file stream for writing
        """
        fout.write("\t&SUBSYS\n")
        if self.kind.status == True:
            self.kind.to_input(fout, self.xyz)
        if self.cell.status == True:
            self.cell.to_input(fout, self.xyz)
        if self.topology.status == True:
            self.topology.to_input(fout, self.xyz)
        fout.write("\t&END SUBSYS\n")

        
