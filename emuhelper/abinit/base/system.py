#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import pymatgen as mg

from emuhelper.base.xyz import base_xyz


class abinit_system:
    """
    """
    def __init__(self, xyz_f):
        self.xyz = base_xyz(xyz_f)

    def to_in(self, fout):
        # fout: a file stream for writing
        cell = self.xyz.cell
        fout.write("acell 1 1 1\n")  # scaling with 1 means no actually scaling of rprim by acell
        fout.write("rprim\n")
        fout.write("%f %f %f\n" % (cell[0], cell[1], cell[2]))
        fout.write("%f %f %f\n" % (cell[3], cell[4], cell[5]))
        fout.write("%f %f %f\n" % (cell[6], cell[7], cell[8]))
        fout.write("ntypat %d\n" % self.xyz.nspecies)
        fout.write("natom %d\n" % self.xyz.natom)
        fout.write("typat\n")
        # abinit 不允许输入文件列数超过264, 因此如果原子数太多
        # 这里的typat要分多行列出
        # 利用余数设置如果一行超过30个原子就换行
        i = 0 
        for atom in self.xyz.atoms:
            fout.write("%d " % self.xyz.specie_labels[atom.name])
            if i % 30 == 29:
                fout.write("\n")
            i += 1
        fout.write("\n")
        fout.write("znucl ")
        for element in self.xyz.specie_labels:
            fout.write(str(mg.Element[element].number))
            fout.write(" ")
        fout.write("\n")
        fout.write("\n")
        fout.write("xangst\n")
        for atom in self.xyz.atoms:
            fout.write("%f %f %f\n" % (atom.x, atom.y, atom.z))
        fout.write("\n")
        #
