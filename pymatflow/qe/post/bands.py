#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os


def calc_carrier_effective_mass():
    pass

def calc_band_gap():
    pass

class bands_post:
    """
    """
    def __init__(self, pwxbandsin, bandsxout):
        """
        pwxbandin:
            the input file for the pw.x band calculation. used to get the special kpoints names.
        bandsxout:
            used to get the x coordinate of the special kpoints

        specialk:
            [{label: "Gamma", coord: [float, float, float], xcoord: float}, ....]
            coord is the kpoint coordinate specified in pw.x band calculation
            xcoord is the correspondin x coordinates for the special kpoint in
            band plot(read from the band.x calculation output: x coordinate)
        """
        with open(pwxbandsin, 'r') as fout:
            self.pwxbandsin = fout.readlines()
        with open(bandsxout, 'r') as fout:
            self.bandsxout = fout.readlines()

        self.specialk = []
        self.bandfile_gnu = None
        self.get_info()

    def get_info(self):
        # get the special kpoint coord and label from pw.x band calculation input file
        nspecialk = 0
        special_k_begin = 0
        special_k_end = 0
        for i in range(len(self.pwxbandsin)):
            if len(self.pwxbandsin[i].split()) == 0:
                continue
            if self.pwxbandsin[i].split()[0] == "K_POINTS":
                nspecialk = int(self.pwxbandsin[i+1].split()[0])
                special_k_begin = i + 2
                special_k_end = i + 1 + nspecialk

        for i in range(special_k_begin, special_k_end + 1):
            print(self.pwxbandsin[i].split("#"))
            kpoint = {"label": self.pwxbandsin[i].split("#")[1].split()[0], "coord": [float(self.pwxbandsin[i].split()[0]), float(self.pwxbandsin[i].split()[1]), float(self.pwxbandsin[i].split()[2])], "xcoord": None}
            self.specialk.append(kpoint)

        # get the x coordinate from band.x output file
        xcoord_begin = 0
        for i in range(len(self.bandsxout)):
            if len(self.bandsxout[i].split()) == 0:
                continue
            if self.bandsxout[i].split()[0] == "high-symmetry":
                xcoord_begin = i
                break # break for loop in the first high-symmetry
        for i in range(nspecialk):
            print(self.bandsxout[xcoord_begin+i])
            self.specialk[i]["xcoord"] = float(self.bandsxout[xcoord_begin+i].split()[-1].split("\n")[0])
        #
        # get the xxx.data.gnu file names and xxx.dat file names
        for line in self.bandsxout:
            if len(line.split()) == 0:
                continue
            if line.split()[0] == "Plottable":
                self.bandfile_gnu = line.split()[6] # energy in eV
            if line.split()[0] == "Bands" and line.split()[1] == "written":
                self.bandfile_dat = line.split()[4]
        #
        # get fermi energy from nscf output
        scfout = "static-scf.out"
        nscfout = "static-nscf.out"
        if os.path.exists(os.path.join("./", nscfout)):
            with open(os.path.join("./", nscfout), 'r') as fin:
                for line in fin:
                    if len(line.split()) == 0:
                        continue
                    if line.split()[0] == "the" and line.split()[1] == "Fermi":
                        self.efermi = float(line.split()[4])
        elif os.path.exists(os.path.join("./", scfout)):
            with open(os.path.join("./", scfout), 'r') as fin:
                for line in fin:
                    if len(line.split()) == 0:
                        continue
                    if line.split()[0] == "the" and line.split()[1] == "Fermi":
                        self.efermi = float(line.split()[4])
        else:
            print("===========================================================\n")
            print("                Warning !!!\n")
            print("===========================================================\n")
            print("BAND structure postprocessing:\n")
            print("must provide nscfout or at least scfout to get Fermi energy\n")
            sys.exit(1)
        # we do not directly shift Efermi to zero in the dataset
        # but only use it to set the gnuplot scripts so that gnuplot
        # script will be responsible for shfiting Efermi to zero.

    def plot_band(self, option="gnuplot", bandrange=[0, 1.0]):
        """
        option:
            gnuplot or matplotlib
        bandrange:
            a list of two values(between 0 and 1) defining the percentage
            of bands to plot.
            plotrange[0]: left boundary of the nth band to plot
            plotrange[1]: right boundary of the nth band to plot
            default is plotrange[0] = 0, plotrange[1], in which case
            all the band available will be plot.
            Be aware that the range if not for energy but for band number

            currently bandrange only works when option == 'matplotlib'
        """
        os.system("mkdir -p post-processing")
        if option == "gnuplot":
            # from self.bandfile_gnu build an file contain part all all of the band structure data
            # depending on bandrange
            with open(self.bandfile_dat, 'r') as fout:
                lines = fout.readlines()
                nbnd = int(lines[0].split()[2].split(",")[0])

            with open(self.bandfile_gnu, 'r') as fin:
                band_data_gnu = fin.readlines()
            len_xcoord = 0
            for line in band_data_gnu:
                if len(line.split()) == 0:
                    break
                len_xcoord += 1
            begin = int(nbnd*bandrange[0])
            end = int(nbnd*bandrange[1])
            with open(os.path.join("post-processing", self.bandfile_gnu+".bandrange"), 'w') as fout:
                for i in range(begin, end):
                    for k in range((i*(len_xcoord+1)), i*(len_xcoord+1)+len_xcoord, 1):
                        fout.write(band_data_gnu[k])
                    fout.write("\n")
            #
            with open(os.path.join("post-processing", "bandplot.gp"), 'w') as fout:
                fout.write("set terminal gif\n")
                fout.write("set output 'bandstructure.gif'\n")
                fout.write("unset key\n")
                fout.write("set parametric\n")

                fout.write("set title 'Bandstructure'\n")
                fout.write("set xlabel 'K'\n")
                fout.write("set ylabel 'Energy(eV)'\n")
                #fout.write("set xtics(")
                #for point in self.specialk:
                #    if point["label"] == "GAMMA":
                #        fout.write("'%s' %f, " % ("{/symbol G}", point["xcoord"]))
                #    else:
                #        fout.write("'%s' %f, " % (point["label"], point["xcoord"]))
                #fout.write(")\n")

                locs = [self.specialk[i]["xcoord"] for i in range(len(self.specialk))]
                labels = ["{/symbol G}" if self.specialk[i]["label"] == "GAMMA" else "%s" % self.specialk[i]["label"] for i in range(len(self.specialk))]
                #
                # sometime the xcoord of two specialk might be the same
                # either caused from physical reason or when you specif
                # 0 to connect the two special k point.
                # whatever the reason we should join the two label to one
                # label like K|U
                locs_refined = []
                labels_refined = []
                labels_refined.append(labels[0])
                locs_refined.append(locs[0])
                for i in range(1, len(labels)):
                    if locs[i]  == locs[i-1]:
                        # join labels[i] and labels[i-1]
                        labels_refined[-1] = "%s | %s" % (labels[i-1], labels[i])
                    else:
                        labels_refined.append(labels[i])
                        locs_refined.append(locs[i])
                fout.write("set xtics(")
                for i in range(int(len(labels_refined)-1)):
                    fout.write("'%s' %f, " % (labels_refined[i], locs_refined[i]))
                fout.write("'%s' %f)\n" % (labels_refined[-1], locs_refined[-1]))

                print("===================================================\n")
                print("               post-qe-bands.py\n")
                print("----------------------------------------------------\n")
                print("engine: matplotlib\n")
                print("----------------------------------------------------\n")
                print("Note:\n")
                print("sometime the xcoord of two neighbor specialk might be\n")
                print("the same either from physical reason or when you specify\n")
                print("0 to connect the two special k point in pw.x band calc.\n")
                print("whatever the reason we should join the two label to one\n")
                print("label like K|U\n")
                print("in this way when you want a k path like:\n")
                print("Gamma–X–M–Gamma–Z–R–A–Z|X–R|M–A\n")
                print("you can specify 0 to connect Z and X\n")
                print("and 0 to connect R and M in pw.x band structure calc.\n")
                print("then post-qe-bands.py can deal with that automatically\n")
                print("------------------------------------------------------\n")
                print("original specialk and the correponding xcoord:\n")
                print(locs)
                print(labels)
                print("refined specialk and the corresponding xcoord:\n")
                print(locs_refined)
                print(labels_refined)

                fout.write("set grid xtics ytics\n")
                fout.write("set autoscale\n")
                fout.write("# fermi energy shifted to zero by use using 1:($2-%f) in plot function\n" % self.efermi)
                fout.write("# and data in %s file is not modified at all, and is as it is\n" % self.bandfile_gnu)
                fout.write("plot ")
                fout.write("'%s' using 1:($2-%f) w l" % (self.bandfile_gnu+".bandrange", self.efermi))
                #
                #for i in range(len(self.specialk) - 1):
                #    fout.write(", %f, t" % (self.specialk[i]["xcoord"]))
                #fout.write(", %f, t\n" % self.specialk[-1]["xcoord"])
                #
                fout.write("\n")
            os.chdir("post-processing")
            os.system("gnuplot bandplot.gp")
            os.system("eog bandstructure.gif")
            os.chdir("../")

        elif option == "matplotlib":

            import numpy as np
            import matplotlib.pyplot as plt

            with open(self.bandfile_dat, 'r') as fout:
                lines = fout.readlines()
                nbnd = int(lines[0].split()[2].split(",")[0])
                nks = int(lines[0].split()[4])

            with open(self.bandfile_gnu, 'r') as fout:
                data =  np.loadtxt(fout)

            begin = int(nbnd*bandrange[0])
            end = int(nbnd*bandrange[1])

            for i in range(begin, end):
                # here minus self.efermi means the plot will shift efermi to 0
                # band the data variable is not modified.
                plt.plot(data[i*nks:(i+1)*nks, 0], data[i*nks:(i+1)*nks, 1] - self.efermi)
            plt.title("Band Structure")
            plt.ylabel(r"$\mathit{E}-\mathit{E}_\mathrm{f} (eV)$")
            plt.xlabel("Kpoints")
            plt.grid(which="major", axis="x", linewidth=0.75, linestyle="-", color="0.75")
            plt.grid(which="major", axis="y", linewidth=0.75, linestyle="-", color="0.75")

            locs = [self.specialk[i]["xcoord"] for i in range(len(self.specialk))]
            labels = [r"$\Gamma$" if self.specialk[i]["label"] == "GAMMA" else r"$%s$" % self.specialk[i]["label"] for i in range(len(self.specialk))]
            #plt.xticks(locs, labels)
            #
            # sometime the xcoord of two specialk might be the same
            # either caused from physical reason or when you specif
            # 0 to connect the two special k point.
            # whatever the reason we should join the two label to one
            # label like K|U
            locs_refined = []
            labels_refined = []
            labels_refined.append(labels[0])
            locs_refined.append(locs[0])
            for i in range(1, len(labels)):
                if locs[i]  == locs[i-1]:
                    # join labels[i] and labels[i-1]
                    labels_refined[-1] = r"$%s | %s$" % (labels[i-1].split("$")[1], labels[i].split("$")[1])
                else:
                    labels_refined.append(labels[i])
                    locs_refined.append(locs[i])
            print("===================================================\n")
            print("               post-qe-bands.py\n")
            print("----------------------------------------------------\n")
            print("engine: matplotlib\n")
            print("----------------------------------------------------\n")
            print("Note:\n")
            print("sometime the xcoord of two neighbor specialk might be\n")
            print("the same either from physical reason or when you specify\n")
            print("0 to connect the two special k point in pw.x band calc.\n")
            print("whatever the reason we should join the two label to one\n")
            print("label like K|U\n")
            print("in this way when you want a k path like:\n")
            print("Gamma–X–M–Gamma–Z–R–A–Z|X–R|M–A\n")
            print("you can specify 0 to connect Z and X\n")
            print("and 0 to connect R and M in pw.x band structure calc.\n")
            print("then post-qe-bands.py can deal with that automatically\n")
            print("------------------------------------------------------\n")
            print("original specialk and the correponding xcoord:\n")
            print(locs)
            print(labels)
            print("refined specialk and the corresponding xcoord:\n")
            print(locs_refined)
            print(labels_refined)
            # ---------------------------------------------------------------
            #plt.xticks(locs, labels) # do not use this, it is unrefined
            plt.xticks(locs_refined, labels_refined)
            #plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join("post-processing", "bandstructure-maplotlib.png"))
            plt.close()
            #
