"""
post_bands:
    now post_bands can extract band data from vasprun.xml, but it suppose
    the kpoints in vasprun.xml are in crystal coordinates. and it will build
    the kpoints length: xcoord_k from the high symmetry line and the corresponding
    basis for reciprocal space.

    actually in vasp reci_basis is the reciprocal of the real space basis, namely
    b1 = 1 / a1, b2 = 1 / a2 and b3 = 1 / a3.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from xml.etree.ElementTree import parse

class post_bands:
    def __init__(self):
        pass

    def get_kpath_and_vasprun(self, kpath, vasprun="vasprun.xml"):
        # vasprun.xml
        self.vasprun = parse(vasprun)

        # kpath
        self.kpath = kpath

        self.get_xcoord_k()
        self.get_eigenval()
        self.efermi = float(self.vasprun.getroot().find("calculation").find("dos").find("i").text)

        self.locs = []
        self.labels_for_matplotlib = []
        self.labels_for_gnuplot = []
        n_div = 0
        for kpoint in self.kpath:
            if kpoint[4] == "|":
                n_div += 1
        n_band_line = len(self.kpath) - 1 - n_div
        intersections = len(self.xcoord_k) / n_band_line
        for i in range(n_band_line):
            print(intersections*i)
            self.locs.append(self.xcoord_k[int(intersections*i)])
        self.locs.append(self.xcoord_k[-1])

        self.labels_for_matplotlib.append(r"$%s$" % self.kpath[0][3].upper() if self.kpath[0][3].upper() != "GAMMA" else r"$\Gamma$")
        self.labels_for_gnuplot.append("%s" % self.kpath[0][3].upper() if self.kpath[0][3].upper() != "GAMMA" else "{/symbol G}")
        for i in range(1, len(self.kpath)):
            if self.kpath[i-1][4] != "|":
                self.labels_for_matplotlib.append(r"$%s$" % self.kpath[i][3].upper() if self.kpath[i][3].upper() != "GAMMA" else r"$\Gamma$")
                self.labels_for_gnuplot.append("%s" % self.kpath[i][3].upper() if self.kpath[i][3].upper() != "GAMMA" else "{/symbol G}")
            else:
                self.labels_for_matplotlib[-1] = r"$%s | %s$" % (self.labels_for_matplotlib[-1].split("$")[1], self.kpath[i][3].upper())
                self.labels_for_gnuplot[-1] = "%s | %s" % (self.labels_for_gnuplot[-1], self.kpath[i][3].upper())

    def get_xcoord_k(self):
        """
        Note:
            xcoord_k is the x axis of the band structure plot
            let's see how it is build from kpoints and the
            crystal lattice or reciprocal lattice.
        """
        self.xcoord_k = []
        # get the lattice parameter and the reciprocal basis
        a1 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[0].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[0].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[0].text.split()[2])**2
                )
        a2 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[1].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[1].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[1].text.split()[2])**2
                )
        a3 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[2].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[2].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[0].getchildren()[2].text.split()[2])**2
                )

        b1 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[0].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[0].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[0].text.split()[2])**2
                )

        b2 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[1].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[1].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[1].text.split()[2])**2
                )

        b3 = np.sqrt(
                float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[2].text.split()[0])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[2].text.split()[1])**2
                + float(self.vasprun.findall("structure")[0].getchildren()[0].getchildren()[2].getchildren()[2].text.split()[2])**2
                )

        # actually you will find that in vasp b1=1/a1, b2=1/a2, b3=1/a3
        # now we use the reciprocal lattice constant and the kpoints in crystal coordinate to build the xcoord_k


        # in the past, we read kpoint from vasprun.xml but now we directly read kpoint from self.kpath!
        self.xcoord_k.append(0.0000000)
        for i in range(1, len(self.kpath)):
            if self.kpath[i-1][4] != "|":
                step = 0
                delta_b_1 = b1 * (self.kpath[i][0] - self.kpath[i-1][0])
                delta_b_2 = b2 * (self.kpath[i][1] - self.kpath[i-1][1])
                delta_b_3 = b3 * (self.kpath[i][2] - self.kpath[i-1][2])
                step = np.sqrt(delta_b_1**2+delta_b_2**2+delta_b_3**2) / (self.kpath[i-1][4] - 1)

                for j in range(self.kpath[i-1][4]-1):
                    self.xcoord_k.append(self.xcoord_k[-1]+step)
                if i == len(self.kpath) - 1:
                    pass
                else:
                    self.xcoord_k.append(self.xcoord_k[-1])
                        
        # the old code to get kpoints from vasprun.xml and build xcoord_k
        #divisions = int(self.vasprun.find("kpoints").find("generation").find("i").text)

        #n_segment = int(len(self.vasprun.find("kpoints").findall("varray")[0].getchildren()) / divisions)

        #for i in range(n_segment):
            # xcoord_k of the first point of each segment equals to the
            # last xcoord_k of the previous segment
        #    if i == 0:
        #        # begin from 0.0000000
        #        self.xcoord_k.append(0.00000000)
        #    else:
        #        self.xcoord_k.append(self.xcoord_k[-1])

            # the step in the xcoord_k for each segment is different and it is actually
            # the distance between the two high symmetry kpoint in unit of reciprocal coordinates
            # divided by (divisions - 1)
        #    step = 0
        #    delta_b_1 = b1*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*divisions].text.split()[0]) - b1*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*15+divisions-1].text.split()[0])

        #    delta_b_2 = b2*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*divisions].text.split()[1]) - b2*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*15+divisions-1].text.split()[1])

        #    delta_b_3 = b3*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*divisions].text.split()[2]) - b3*float(self.vasprun.find("kpoints").findall("varray")[0].getchildren()[i*15+divisions-1].text.split()[2])
        #    step = np.sqrt(delta_b_1**2+delta_b_2**2+delta_b_3**2) / (divisions-1)

        #    for j in range(divisions-1):
        #        self.xcoord_k.append(self.xcoord_k[-1]+step)

    def get_eigenval(self):
        """

        """
        # first check the magnetic_status
        for i in range(len(self.vasprun.getroot().find("parameters"))):
            if self.vasprun.getroot().find("parameters").getchildren()[i].attrib["name"] == "electronic":
                for item in self.vasprun.getroot().find("parameters")[i]:
                    if item.attrib["name"] == "electronic spin":
                        for spin_item in item:
                            if spin_item.attrib["name"] == "ISPIN":
                                ispin = int(spin_item.text.split()[0])
                            elif spin_item.attrib["name"] == "LNONCOLLINEAR":
                                lnoncollinear = spin_item.text.split()[0]
                            elif spin_item.attrib["name"] == "LSORBIT":
                                lsorbit = spin_item.text.split()[0]
        if lsorbit == "T":
            self.magnetic_status = "soc-ispin-%d" % ispin # soc-ispin-1 or soc-ispin-2
        else:
            self.magnetic_status = "non-soc-ispin-%d" % ispin # non-soc-ispin-1 or non-soc-ispin-2


        # get the eigenval
        if self.magnetic_status == "non-soc-ispin-1":
            # get only one spin
            self.eigenval = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[0]:
                self.eigenval.append({})
                self.eigenval[-1]["energy"] = []
                self.eigenval[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            # if HSE is used, in pymatflow the kpoints in the KPOINTS file include the Monkhorst-pack from SCF and 
            # kpoints from kpath. so self.eigeval contains data for both the two part of kpoints.
            # here we remove the Monkhorst-pack part kpoint from self.eigenval.
            nk_scf = len(self.eigenval) -  len(self.xcoord_k)
            for i in range(nk_scf):
                self.eigenval[i] = None
            for i in range(nk_scf):
                self.eigenval.remove(None)
        elif self.magnetic_status == "non-soc-ispin-2":
            # need to get two spin data set
            self.eigenval_spin1 = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[0]:
                self.eigenval_spin1.append({})
                self.eigenval_spin1[-1]["energy"] = []
                self.eigenval_spin1[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval_spin1[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval_spin1[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            self.eigenval_spin2 = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[1]:
                self.eigenval_spin2.append({})
                self.eigenval_spin2[-1]["energy"] = []
                self.eigenval_spin2[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval_spin2[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval_spin2[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            # if HSE is used, in pymatflow the kpoints in the KPOINTS file include the Monkhorst-pack from SCF and 
            # kpoints from kpath. so self.eigeval contains data for both the two part of kpoints.
            # here we remove the Monkhorst-pack part kpoint from self.eigenval.
            nk_scf = len(self.eigenval_spin1) -  len(self.xcoord_k)
            for i in range(nk_scf):
                self.eigenval_spin1[i] = None
                self.eigenval_spin2[i] = None
            for i in range(nk_scf):
                self.eigenval_spin1.remove(None)
                self.eigenval_spin2.remove(None)
        elif self.magnetic_status == "soc-ispin-1":
            # need to get four spin data set
            self.eigenval_spin1 = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[0]:
                self.eigenval_spin1.append({})
                self.eigenval_spin1[-1]["energy"] = []
                self.eigenval_spin1[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval_spin1[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval_spin1[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            # if HSE is used, in pymatflow the kpoints in the KPOINTS file include the Monkhorst-pack from SCF and 
            # kpoints from kpath. so self.eigeval contains data for both the two part of kpoints.
            # here we remove the Monkhorst-pack part kpoint from self.eigenval.
            nk_scf = len(self.eigenval_spin1) -  len(self.xcoord_k)
            for i in range(nk_scf):
                self.eigenval_spin1[i] = None
            for i in range(nk_scf):
                self.eigenval_spin1.remove(None)
        elif self.magnetic_status == "soc-ispin-2":
            # need to get four spin data set
            self.eigenval_spin1 = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[0]:
                self.eigenval_spin1.append({})
                self.eigenval_spin1[-1]["energy"] = []
                self.eigenval_spin1[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval_spin1[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval_spin1[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            self.eigenval_spin2 = []
            for kpoint in self.vasprun.getroot().find("calculation").find("eigenvalues").find("array").findall("set")[0].findall("set")[1]:
                self.eigenval_spin2.append({})
                self.eigenval_spin2[-1]["energy"] = []
                self.eigenval_spin2[-1]["occupation"] = []
                for i in range(len(kpoint)):
                    self.eigenval_spin2[-1]["energy"].append(float(kpoint[i].text.split()[0]))
                    self.eigenval_spin2[-1]["occupation"].append(float(kpoint[i].text.split()[1]))
            # if HSE is used, in pymatflow the kpoints in the KPOINTS file include the Monkhorst-pack from SCF and 
            # kpoints from kpath. so self.eigeval contains data for both the two part of kpoints.
            # here we remove the Monkhorst-pack part kpoint from self.eigenval.
            nk_scf = len(self.eigenval_spin1) -  len(self.xcoord_k)
            for i in range(nk_scf):
                self.eigenval_spin1[i] = None
                self.eigenval_spin2[i] = None
            for i in range(nk_scf):
                self.eigenval_spin1.remove(None)
                self.eigenval_spin2.remove(None)

    def _plot_band_matplotlib(self, bandrange=[0, 1.0]):
        """
        :param bandrange:
            a list of two values(between 0 and 1) defining the percentage
            of bands to plot.
            plotrange[0]: left boundary of the nth band to plot
            plotrange[1]: right boundary of the nth band to plot
            default is plotrange[0] = 0, plotrange[1], in which case
            all the band available will be plot.
            Be aware that the range if not for energy but for band number
        :param imagebase: image file name(not full)
        """

        if self.magnetic_status == "non-soc-ispin-1":
            nband = len(self.eigenval[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval[k]["energy"][i] - self.efermi for k in range(len(self.eigenval))], color='blue', linewidth=1)
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.title("Band Structure")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-%s.png" % slef.magnetic_status)
            plt.close()
        if self.magnetic_status == "non-soc-ispin-2":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin1[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin1))])
            plt.title("Band Structure(Spin 1)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-%s-spin-1.png" % self.magnetic_status)
            plt.close()
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin2[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin2))])
            plt.title("Band Structure(Spin 2)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-%s-spin-2.png" % self.magnetic_status)
            plt.close()
            # all spin in on figure
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin1[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin1))])
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin2[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin2))])
            plt.title("Band Structure(all spin)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-%s-spin-all.png" % self.magnetic_status)
            plt.close()

        if self.magnetic_status == "soc-ispin-1":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin1[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin1))])
            plt.title("Band Structure")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-soc-ispin-1.png")
            plt.close()

        if self.magnetic_status == "soc-ispin-2":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin1[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin1))])
            plt.title("Band Structure(Spin 1)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-soc-ispin-2-spin-1.png")
            plt.close()
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin2[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin2))])
            plt.title("Band Structure(Spin 2)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-soc-ispin-2-spin-2.png")
            plt.close()                
            # all spin in on figure
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin1[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin1))])
            for i in range(band_min, band_max, 1):
                plt.plot(self.xcoord_k, [self.eigenval_spin2[k]["energy"][i] - self.efermi for k in range(len(self.eigenval_spin2))])
            plt.title("Band Structure(all spin)")
            plt.xlabel("K")
            plt.ylabel("Energy(eV)")
            plt.xticks(self.locs, self.labels_for_matplotlib)
            plt.grid(b=True, which='major')
            plt.savefig("band-structure-soc-ispin-2-spin-all.png")
            plt.close()     


    def _plot_band_gnuplot(self, bandrange=[0, 1.0]):
        """
        :param bandrange:
            a list of two values(between 0 and 1) defining the percentage
            of bands to plot.
            plotrange[0]: left boundary of the nth band to plot
            plotrange[1]: right boundary of the nth band to plot
            default is plotrange[0] = 0, plotrange[1], in which case
            all the band available will be plot.
            Be aware that the range if not for energy but for band number
        :param imagebase: image file name(not full)
        """

        if self.magnetic_status == "non-soc-ispin-1":
            nband = len(self.eigenval[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)
            with open("all-bands-%s.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval[j]["energy"][i]))
                    fout.write("\n")
            with open("specified-bands-%s.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval[j]["energy"][i]))
                    fout.write("\n")

            with open("all-bands-%s.gnuplot" % self.magnetic_status, 'w') as fout:
                fout.write("set terminal gif\n")
                fout.write("set output 'all-bands-%s.gif'\n" % self.magnetic_status)
                fout.write("unset key\n")
                fout.write("set parametric\n")
                fout.write("set title 'Band Structure'\n")
                fout.write("set xlabel 'K'\n")
                fout.write("set ylabel 'Energy(eV)'\n")
                fout.write("set xtics(")
                for i in range(len(self.labels_for_gnuplot)-1):
                    fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                fout.write("set grid xtics ytics\n")
                fout.write("set autoscale\n")
                fout.write("plot 'all-bands-spin-unpolarized.data' using 1:($2-%f) w l\n" % self.efermi)
            os.system("gnuplot all-bands-spin-unpolarized.gnuplot")

            with open("specified-bands-%s.gnuplot" % self.magnetic_status, 'w') as fout:
                fout.write("set terminal gif\n")
                fout.write("set output 'specified-bands-%s.gif'\n" % self.magnetic_status)
                fout.write("unset key\n")
                fout.write("set parametric\n")
                fout.write("set title 'Band Structure'\n")
                fout.write("set xlabel 'K'\n")
                fout.write("set ylabel 'Energy(eV)'\n")
                fout.write("set xtics(")
                for i in range(len(self.labels_for_gnuplot)-1):
                    fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                fout.write("set grid xtics ytics\n")
                fout.write("set autoscale\n")
                fout.write("plot 'specified-bands-%s.data' using 1:($2-%f) w l\n" % (self.magnetic_status, self.efermi))
            os.system("gnuplot specified-bands-%s.gnuplot" % self.magnetic_status)

        if self.magnetic_status == "non-soc-ispin-2":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)

            with open("all-bands-%s-spin-1.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")

            with open("all-bands-%s-spin-2.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin2[j]["energy"][i]))
                    fout.write("\n")

            with open("specified-bands-%s-spin-1.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")

            with open("specified-bands-%s-spin-2.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin2[j]["energy"][i]))
                    fout.write("\n")


            for k in range(2):
                with open("all-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1), 'w') as fout:
                    fout.write("set terminal gif\n")
                    fout.write("set output 'all-bands-%s-spin-%d.gif'\n" % (self.magnetic_status, k+1))
                    fout.write("unset key\n")
                    fout.write("set parametric\n")
                    fout.write("set title 'Band Structure'\n")
                    fout.write("set xlabel 'K'\n")
                    fout.write("set ylabel 'Energy(eV)'\n")
                    fout.write("set xtics(")
                    for i in range(len(self.labels_for_gnuplot)-1):
                        fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                    fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                    fout.write("set grid xtics ytics\n")
                    fout.write("set autoscale\n")
                    fout.write("plot 'all-bands-%s-spin-%d.data' using 1:($2-%f) w l\n" % (self.magnetic_status, k+1, self.efermi))
                os.system("gnuplot all-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1))


                with open("specified-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1), 'w') as fout:
                    fout.write("set terminal gif\n")
                    fout.write("set output 'specified-bands-%s-spin-%d.gif'\n" % (self.magnetic_status, k+1))
                    fout.write("unset key\n")
                    fout.write("set parametric\n")
                    fout.write("set title 'Band Structure'\n")
                    fout.write("set xlabel 'K'\n")
                    fout.write("set ylabel 'Energy(eV)'\n")
                    fout.write("set xtics(")
                    for i in range(len(self.labels_for_gnuplot)-1):
                        fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                    fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                    fout.write("set grid xtics ytics\n")
                    fout.write("set autoscale\n")
                    fout.write("plot 'specified-bands-%s-spin-%d.data' using 1:($2-%f) w l\n" % (self.magnetic_status, k+1, self.efermi))
                os.system("gnuplot specified-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1))


        if self.magnetic_status == "soc-ispin-1":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)

            with open("all-bands-%s.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")         

            with open("specified-bands-%s.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")           

            with open("all-bands-%s.gnuplot" % self.magnetic_status, 'w') as fout:
                fout.write("set terminal gif\n")
                fout.write("set output 'all-bands-%s.gif'\n" % self.magnetic_status)
                fout.write("unset key\n")
                fout.write("set parametric\n")
                fout.write("set title 'Band Structure'\n")
                fout.write("set xlabel 'K'\n")
                fout.write("set ylabel 'Energy(eV)'\n")
                fout.write("set xtics(")
                for i in range(len(self.labels_for_gnuplot)-1):
                    fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                fout.write("set grid xtics ytics\n")
                fout.write("set autoscale\n")
                fout.write("plot 'all-bands-%s.data' using 1:($2-%f) w l\n" % (self.magnetic_status, self.efermi))
            os.system("gnuplot all-bands-%s.gnuplot" % self.magnetic_status)


            with open("specified-bands-%s.gnuplot" % self.magnetic_status, 'w') as fout:
                fout.write("set terminal gif\n")
                fout.write("set output 'specified-bands-%s.gif'\n" % self.magnetic_status)
                fout.write("unset key\n")
                fout.write("set parametric\n")
                fout.write("set title 'Band Structure'\n")
                fout.write("set xlabel 'K'\n")
                fout.write("set ylabel 'Energy(eV)'\n")
                fout.write("set xtics(")
                for i in range(len(self.labels_for_gnuplot)-1):
                    fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                fout.write("set grid xtics ytics\n")
                fout.write("set autoscale\n")
                fout.write("plot 'specified-bands-%s.data' using 1:($2-%f) w l\n" % (self.magnetic_status, self.efermi))
            os.system("gnuplot specified-bands-%s.gnuplot" % self.magnetic_status)

        if self.magnetic_status == "soc-ispin-2":
            nband = len(self.eigenval_spin1[0]["energy"])
            band_min = int(bandrange[0] * nband)
            band_max = int(bandrange[1] * nband)

            with open("all-bands-%s-spin-1.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")

            with open("all-bands-%s-spin-2.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(nband):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin2[j]["energy"][i]))
                    fout.write("\n")

            with open("specified-bands-%s-spin-1.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin1[j]["energy"][i]))
                    fout.write("\n")

            with open("specified-bands-%s-spin-2.data" % self.magnetic_status, 'w') as fout:
                fout.write("# band structure extracted from vasprun.xml\n")
                fout.write("# efermi: %f\n" % self.efermi)
                for i in range(band_min, band_max, 1):
                    for j in range(len(self.xcoord_k)):
                        fout.write("%f %f\n" % (self.xcoord_k[j], self.eigenval_spin2[j]["energy"][i]))
                    fout.write("\n")
  
            for k in range(2):
                with open("all-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1), 'w') as fout:
                    fout.write("set terminal gif\n")
                    fout.write("set output 'all-bands-%s-spin-%d.gif'\n" % (self.magnetic_status, k+1))
                    fout.write("unset key\n")
                    fout.write("set parametric\n")
                    fout.write("set title 'Band Structure'\n")
                    fout.write("set xlabel 'K'\n")
                    fout.write("set ylabel 'Energy(eV)'\n")
                    fout.write("set xtics(")
                    for i in range(len(self.labels_for_gnuplot)-1):
                        fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                    fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                    fout.write("set grid xtics ytics\n")
                    fout.write("set autoscale\n")
                    fout.write("plot 'all-bands-%s-spin-%d.data' using 1:($2-%f) w l\n" % (self.magnetic_status, k+1, self.efermi))
                os.system("gnuplot all-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1))
         

                with open("specified-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1), 'w') as fout:
                    fout.write("set terminal gif\n")
                    fout.write("set output 'specified-bands-%s-spin-%d.gif'\n" % (self.magnetic_status, k+1))
                    fout.write("unset key\n")
                    fout.write("set parametric\n")
                    fout.write("set title 'Band Structure'\n")
                    fout.write("set xlabel 'K'\n")
                    fout.write("set ylabel 'Energy(eV)'\n")
                    fout.write("set xtics(")
                    for i in range(len(self.labels_for_gnuplot)-1):
                        fout.write("'%s' %f, " % (self.labels_for_gnuplot[i], self.locs[i]))
                    fout.write("'%s' %f)\n" % (self.labels_for_gnuplot[-1], self.locs[-1]))
                    fout.write("set grid xtics ytics\n")
                    fout.write("set autoscale\n")
                    fout.write("plot 'specified-bands-%s-spin-%d.data' using 1:($2-%f) w l\n" % (self.magnetic_status, k+1, self.efermi))
                os.system("gnuplot specified-bands-%s-spin-%d.gnuplot" % (self.magnetic_status, k+1))

    def plot_band(self, option="matplotlib", bandrange=[0, 1.0]):
        """
        :parama option:
            gnuplot or matplotlib
        :param bandrange:
            a list of two values(between 0 and 1) defining the percentage
            of bands to plot.
            plotrange[0]: left boundary of the nth band to plot
            plotrange[1]: right boundary of the nth band to plot
            default is plotrange[0] = 0, plotrange[1], in which case
            all the band available will be plot.
            Be aware that the range if not for energy but for band number
        :param imagebase: image file name(not full)
        """
        if option == "matplotlib":
            self._plot_band_matplotlib(bandrange=bandrange)
        elif option == "gnuplot":
            self._plot_band_gnuplot(bandrange=bandrange)
        #

    def export(self, directory="tmp-vasp-static", bandrange=[0, 1], option="matplotlib"):
        """
        :parama option:
            gnuplot or matplotlib
        :param bandrange:
            a list of two values(between 0 and 1) defining the percentage
            of bands to plot.
            plotrange[0]: left boundary of the nth band to plot
            plotrange[1]: right boundary of the nth band to plot
            default is plotrange[0] = 0, plotrange[1], in which case
            all the band available will be plot.
            Be aware that the range if not for energy but for band number
        """
        os.system("mkdir -p %s/post-processing" % directory)
        os.chdir(os.path.join(directory, "post-processing"))
        self.plot_band(option=option,  bandrange=bandrange)
        os.chdir("../../")
