
import os
import shutil


class abinit_files:
    """
    """
    def __init__(self):
        self.name = "abinit.files"
        self.main_in = "abinit.in"
        self.main_out = "abinit.out"
        self.wavefunc_in = "abinit-i"
        self.wavefunc_out = "abinit-o"
        self.tmp = "tmp"

    def to_files(self, fout, system):
        """
        system is an instance of abinit.base.system.abinit_system
        """
        fout.write("%s\n" % self.main_in)
        fout.write("%s\n" % self.main_out)
        fout.write("%s\n" % self.wavefunc_in)
        fout.write("%s\n" % self.wavefunc_out)
        fout.write("%s\n" % self.tmp)
        for element in system.xyz.specie_labels:
            fout.write("%s\n" % (element + ".psp8"))
            #fout.write("%s\n" % (element + ".GGA_PBE-JTH.xml"))
    #
    #
