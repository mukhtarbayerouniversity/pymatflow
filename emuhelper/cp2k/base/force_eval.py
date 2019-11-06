#!/usr/bin/evn python
# _*_ coding: utf-8 _*_

import numpy as np
import sys
import os
import shutil
import pymatgen as mg

from emuhelper.cp2k.base.subsys import cp2k_subsys
from emuhelper.cp2k.base.dft import cp2k_dft

"""
Usage:
"""

class cp2k_force_eval:
    """
    Note:
        注意cp2k_force_eval与cp2k_dft和cp2k_subsys的关系是have a
        而不是is kind of a. 因此这里采用的是组合的方式.
    """
    def __init__(self, xyz_f):
        self.subsys = cp2k_subsys(xyz_f)
        self.dft = cp2k_dft()
        self.params = {
                "METHOD": "QS",
                "EMBED": None,
                "STRESS_TENSOR": None,
                }
        self.check_spin()

    def to_input(self, fout):
        fout.write("&FORCE_EVAL\n")
        for item in self.params:
            if self.params[item] is not None:
                fout.write("\t%s %s\n" % (item, self.params[item]))
        self.subsys.to_subsys(fout)
        self.dft.to_dft(fout)
        fout.write("&END FORCE_EVAL\n") 
        fout.write("\n")
    
    def check_spin(self):
        """
        调用self.dft的check_spin()函数
        """
        self.dft.check_spin(self.subsys.xyz)

    def basic_setting(self):
        self.dft.mgrid.params["CUTOFF"] = 100
        self.dft.mgrid.params["REL_CUTOFF"]= 60

    def set_params(self, params):
        """
        parameters for sub section(like dft), are handled over 
        to sub section controllers.
        """
        for item in params:
            if len(item.split("-")) == 1:
                self.params[item.split("-")[-1]] = params[item]
            elif item.split("-")[0] == "DFT":
                self.dft.set_params({item: params[item]})
