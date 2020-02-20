"""
DFPT calc
"""
import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt

from pymatflow.remote.server import server_handle

from pymatflow.qe.base.control import qe_control
from pymatflow.qe.base.system import qe_system
from pymatflow.qe.base.electrons import qe_electrons
from pymatflow.qe.base.arts import qe_arts


class dfpt_run:
    """
    About:
        dfpt_run implements the control over ph.x, dynmat.x, q2r.x,
        matdyn.x, plotband.x
        calculations based on them.
    Status:
        currently implemented calculation including:
            phx, q2r, matdyn, plotband,
            dynmat, ir_raman, fermi_surface,
    Note:
        ph.x calculation cannot start from pw.x data using Gamma-point
        tricks. so the static scf must be done not using Gamma kpoint
        scheme.

    occupations setting:

        ph.x calculation can not be going when the system is metallic,

        but I found even when my fermi energy is in the gap, ph.x can sometimes fail to run.
        this might result from use of smearing in the scf calculation. we should tray other type of occupation.

        sometimes ph.x can run when I use smearing type occupation,
        but somtimes it might warning it is metallic, and stop the calculation,
        even thought I found the fermi energy is actually in the gap(insulator).

        DFPT with the Blochl correction of occupation(tetrahedra) is not implemented
        but tetrahedra_opt and fixed is ok.

        for some systems if you do not use smearing occupations, during
        the scf ground state calculation qe will stop, signaling:
        'charge is wrong: smearing is needed'
        but actually in reality we know the system is an insulator.

        2D materials:
        to properly deal with 2D materials, we have to set assume_isolated='2D' in
        pw.x scf calculation and set loto_2d=.true. in q2r.x and matdyn.x calculation
    """
    def __init__(self):
        self.control = qe_control()
        self.system = qe_system()
        self.electrons = qe_electrons()
        self.arts = qe_arts()

        self.control.basic_setting("scf")
        self.electrons.basic_setting()

        self.set_inputph() # default setting

        self._initialize()

    def _initialize(self):
        """ initialize the current object, do some default setting
        """
        self.run_params = {}
        self.set_run()

    def set_run(self, mpi="", server="pbs", jobname="qe", nodes=1, ppn=32):
        """ used to set  the parameters controlling the running of the task
        :param mpi: you can specify the mpi command here, it only has effect on native running

        """
        self.run_params["server"] = server
        self.run_params["mpi"] = mpi
        self.run_params["jobname"] = jobname
        self.run_params["nodes"] = nodes
        self.run_params["ppn"] = ppn

    def get_xyz(self, xyzfile):
        """
        :param xyzfile:
            a modified xyz formatted file(the second line specifies the cell of the
            system).
        """
        self.arts.xyz.get_xyz(xyzfile)
        self.system.basic_setting(self.arts)
        self.arts.basic_setting(ifstatic=True)

    def set_inputph(self, inputph={}):
        """
        Reference:
            https://gitlab.com/QEF/material-for-ljubljana-qe-summer-school/blob/master/Day-3/handson-day3-DFPT.pdf
            http://www.quantum-espresso.org/Doc/ph_user_guide/
            http://www.fisica.uniud.it/~giannozz/QE-Tutorial/handson_phon.html

        ph.x:
            performing phonon calculation based on scf using
            DFPT theory. it is the executable of PHonon package
            if qe.

            parameter epsil = .true. will calculate and store the
            dielectric tensor and effective charges which is for
            the polar materials

            we can do phonon calculation only at \Gamma point and also
            at a q-grid to get a phonon dispersion graph

        Note:
            PHonon: linear-response calculations(phonons, dielectric properties)
                (1) phonon frequencies and eigenvectors at a generic wave vector
                (2) dielectric tensor, effective charges, IR cross sections
                (3) interatomic force constants in real space
                (4) electron-phonon interaction coefficients for metals
                (5) nonresonant Raman cross sections
                (6) third-order anharmonic phonon lifetimes cross sections

            we will always not set amass(i) in ph.x calculation, as ph.x actually
            will read amass from the data file generated by scf calculation!!!

        :param inputph:
            if the value of any of nq1 nq2 nq3 is 0 in self.inputph[""],
            the self.phx function will think we are chooseing gamma point to do
            the calculation. so this allows us to control type of calculation
            on qpoints setting.
            gamma point only: makre sure at least one value of nq1 nq2 nq3 in self.inputph is 0
            qpoints mesh: all value of nq1 nq2 nq3 in self.inputph is nonezero.
        """
        self.inputph = {
                "outdir": self.control.params["outdir"],
                "prefix": self.control.params["prefix"],
                "fildyn": "phx.dyn",
                "tr2_ph": 1.0e-14,
                "nmix_ph": 4, # default value
                "trans": ".true.", # default value
                "lrpa": None,
                "lnoloc": None,
                "nq1": 0,
                "nq2": 0,
                "nq3": 0,
                }
        # ldisp and nogg is not allowed to be set through inputph
        if "ldisp" in inputph or "nogg" in inputph:
            print("===========================================\n")
            print("                  Warning\n")
            print("-------------------------------------------\n")
            print("ldisp and nogg are not allowed to be set\n")
            print("through dfpt.set_inputph\n")
            print("-------------------------------------------\n")
            sys.exit(1)
        # set the self.inputph through inputpp
        for item in inputph:
            self.inputph[item] = inputph[item]


    def phx(self, directory="tmp-qe-static", inpname="phx.in", output="phx.out", runopt="gen", auto=0):
        """
        """
        # ---------------------------------------------------------------
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("ph.x calculation:\n")
            print("  directory of previous scf or nscf calculattion not found!\n")
            sys.exit(1)
        if runopt == "gen" or runopt == "genrun":
            with open(os.path.join(directory, inpname), 'w') as fout:
                fout.write("ph.x calculation\n")
                fout.write("&inputph\n")
                for item in self.inputph:
                    if item in ["nq1", "nq2", "nq3"]:
                        continue  # handled individually
                    if self.inputph[item] is not None:
                        if type(self.inputph[item]) == str and item != "trans" and item != "epsil":
                            fout.write("%s = '%s'\n" % (item, str(self.inputph[item])))
                        else:
                            fout.write("%s = %s\n" % (item, str(self.inputph[item])))
                #
                if not 0 in [self.inputph["nq1"], self.inputph["nq2"], self.inputph["nq3"]]:
                    fout.write("nq1 = %d\n" % self.inputph["nq1"])
                    fout.write("nq2 = %d\n" % self.inputph["nq2"])
                    fout.write("nq3 = %d\n" % self.inputph["nq3"])
                    fout.write("ldisp = .true.\n") # must be set for q mesh calculation
                # get info about atom fixation
                nat_todo = 0
                for atom in self.arts.xyz.atoms:
                    if False in atom.fix:
                        nat_todo += 1

                if nat_todo == self.arts.xyz.natom:
                    fout.write("nat_todo = 0\n") # displace all atoms
                    fout.write("nogg = .false.\n")
                else:
                    fout.write("nat_todo = %d\n" % nat_todo)
                    fout.write("nogg = .true.\n")
                    # gamma_gamma tricks with nat_todo != 0 not available,
                    # so we must use nogg = .true.
                fout.write("/\n")
                # calculation using gamma point only
                if 0 in [self.inputph["nq1"], self.inputph["nq2"], self.inputph["nq3"]]:
                    fout.write("0.0 0.0 0.0\n")
                else:
                    pass
                # indicies of atom to be used in the calculation
                if nat_todo < self.arts.xyz.natom:
                    for i in range(self.arts.xyz.natom):
                        if False in self.arts.xyz.atoms[i].fix:
                            fout.write("%d " % (i+1))
                    fout.write("\n")
                # end incicies for atoms to be used in the calculation
                fout.write("\n")

            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="ph.x")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="ph.x", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])

        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("%s ph.x < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="phx", server=self.run_params["server"])


    def set_q2r(self, q2r_input={}, dynamat_file="phx.dyn", ifc_file="q2r.fc", mpi="", runopt="gen", zasr='simple'):
        """
        q2r.x:
            calculation of Interatomic Force Constants(IFC) from
            Dynamical matrices from the phonon calculation
        """
        self.q2r_input = {
                "fildyn": "phx.dyn", # Dynamical matrices from the phonon calculation
                "zasr": "simple", # A way to impose the acoustic sum rule
                "flfrc": "q2r.fc", # Output file of the interatomic force constants
                }
        for item in q2r_input:
            self.q2r_input[item] = q2r_input[item]

    def q2r(self, directory="tmp-qe-static", inpname="q2r.in", output="q2r.out", runopt="gen", auto=0):
        """
        q2r.x:
            calculation of Interatomic Force Constants(IFC) from
            Dynamical matrices from the phonon calculation
        """
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("q2r calculation:\n")
            print("  directory of previous scf or nscf calculattion not found!\n")
            sys.exit(1)
        if runopt == "gen" or runopt == "genrun":
            with open(os.path.join(directory, inpname), 'w') as fout:
                fout.write("&input\n")
                for item in self.q2r_input:
                    if self.q2r_input[item] is not None:
                        if type(self.q2r_input[item]) == str:
                            fout.write("%s = '%s'\n" % (item, self.q2r_input[item]))
                        else:
                            fout.write("%s = %s\n" % (item, self.q2r_input[item]))
                fout.write("/\n")
                fout.write("\n")
            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="q2r.x")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="q2r.x", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])

        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("%s q2r.x < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="q2r", server=self.run_params["server"])

    def set_matdyn(self, matdyn_input={}, qpoints=None):
        """
        # qpoints is in format like this:
        # [[kx, ky, kz, xcoord, label], ...] like [[0.0, 0,0, 0.0, 0.0, 'GAMMA']]
        # if the label is a str like 'GAMMA', 'K', etc, the q point is a specialk,
        # if the label is None, then the q points is not a specialk

        matdyn.x
            Calculate phonons at generic q points using IFC
        if Born effective charge Z* not found in output ifc file of q2r.x q2r.fc
        TO-LO splittting at q=0 will be absent! and
        if Adirection for q wast not specified: TO-LO splitting will be absent!

        Note:
            a good way is to obtain the qpoints through k points in qe band calculation
            when you define the k points line defined by high symmetry k point in
            band structure calculation, the bands.x output file will contains all
            the kpoints used in addition to the high symmetry k point, and the corresponding
            x coordinates of the high symmetry k point for plot. for x coordinates for
            k points other than high symmetry k point, refer to the output band structure data
            of bands.x in gnuplot format, the first column is the corresonding x coordinates
            for all the kpoints calculated.
            and this process is achived already by script: pymatflow.qe.scripts.qe-get-matdyn-qpoints-from-bands-calc.py
        """
        self.matdyn_input = {
                "flfrc": "q2r.fc", # File with IFC's
                "asr": "simple", # Acoustic sum rule
                "flfrq": "matdyn.freq",  # Output file with the frequencies
                }
        for item in matdyn_input:
            self.matdyn_input[item] = matdyn_input[item]

        # setting of qpoints
        self.matdyn_qpoints = {
                "qpoint-option": None,
                "nqpoint": len(qpoints),
                "qpoints": qpoints, # [[kx, ky, kz, xcoord, label], ...] like [[0.0, 0,0, 0.0, 0.0, 'GAMMA']]
                }
        # self.matdyn_qpoints["qpoints"] is in format like this:
        # [[kx, ky, kz, xcoord, label], ...] like [[0.0, 0,0, 0.0, 0.0, 'GAMMA']]
        # if the label is a str like 'GAMMA', 'K', etc, the q point is a specialk,
        # if the label is None, then the q points is not a specialk

    def matdyn(self, directory="tmp-qe-static", inpname="matdyn.in", output="matdyn.out", runopt="gen", auto=0):
        """
        """
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("matdyn.x calculation:\n")
            print("  directory of previous scf or nscf calculattion not found!\n")
            sys.exit(1)
        #
        if runopt == "gen" or runopt == "genrun":
            with open(os.path.join(directory, inpname), 'w') as fout:
                fout.write("&input\n")
                for item in self.matdyn_input:
                    if self.matdyn_input[item] is not None:
                        if type(self.matdyn_input[item]) == str:
                            fout.write("%s = '%s'\n" % (item, self.matdyn_input[item]))
                        else:
                            fout.write("%s = %s\n" % (item, self.matdyn_input[item]))
                fout.write("/\n")
                fout.write("%d\n" % self.matdyn_qpoints["nqpoint"]) # Number of q points
                for i in range(self.matdyn_qpoints["nqpoint"]):
                    if self.matdyn_qpoints["qpoints"][i][4] == None:
                        fout.write("%f %f %f %f\n" % (self.matdyn_qpoints["qpoints"][i][0], self.matdyn_qpoints["qpoints"][i][1], self.matdyn_qpoints["qpoints"][i][2], self.matdyn_qpoints["qpoints"][i][3]))
                    else:
                        fout.write("%f %f %f %f #%s\n" % (self.matdyn_qpoints["qpoints"][i][0], self.matdyn_qpoints["qpoints"][i][1], self.matdyn_qpoints["qpoints"][i][2], self.matdyn_qpoints["qpoints"][i][3], self.matdyn_qpoints["qpoints"][i][4]))


            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="matdyn.x")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="matdyn.x", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])
        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("%s matdyn.x < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="matdyn", server=self.run_params["server"])

    def plotband_for_matdyn(self, directory="tmp-qe-static", inpname="plotband.in", output="plotband.out", frequencies_file="matdyn.freq", runopt="gen", freq_min=0, freq_max=600, efermi=0, freq_step=100.0, freq_reference=0.0, auto=0):
        """
        plotband.x
            Plot the phonon dispersion
        Note:
            it seems plotband.x is not implemented parallelly,
            when I use 1 node 32 cores to run it, it will never
            stop.
            so we should alway use one node one core to run it.
        """
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("plotband calculation:\n")
            print("  directory of previous scf or nscf calculattion not found!\n")
            sys.exit(1)
        if runopt == "gen" or runopt == "genrun":
            with open(os.path.join(directory, inpname), 'w') as fout:
                fout.write("%s\n" % frequencies_file) # Input file with the frequencies at various q
                fout.write("%f %f\n" % (freq_min, freq_max)) # Range of frequencies for a visualization
                fout.write("plotband-freq.plot\n") # Output file with frequencies which will be used for plot
                fout.write("plotband-freq.ps\n") # Plot of the dispersion
                fout.write("%f\n" % efermi) # Fermi level (needed only for band structure plot)
                fout.write("%f %f\n" % (freq_step, freq_reference)) # Freq. step and reference freq. on the plotband-flreq.ps

            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="plotband.x")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="plotband.x", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])
        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("%s plotband.x < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="plotband", server=self.run_params["server"])

    def set_dynmat(self, dynmat_input={}):
        """
        imposing acoustic sum rule (ASR)
        extract the phonon information from ph.x output using dynmat.x(
        which can also be used to get IR and Raman.
        the generated fildyn.axsf fildyn.mold can be visualized by xcrysden
        and molden separately, and molden can visualize the vibration through
        fildyn.mold
        )
        Note:
            only used when the ph.x calculation was conducted using Gamma point but not the q mesh.

            q(1) q(2) q(3) are used to get LO-TO splitting.

            dynmat.x will output a file defined by variable fileout, which is dynmat.out
            by default. so we should not redirect the output of dynmat.x running to
            a file with that name. or they might be the same file which should of course
            be avoided.
            and we redirect running output to dynmat-gamma.out and that will not
            affect the default fileout dynmat.out
        """
        self.dynmat_input = {
                "fildyn": "phx.dyn", # File containing the dynamical matrix
                "asr": "simple",
                "q(1)": 0,
                "q(2)": 0,
                "q(3)": 0,
                }
        for item in dynmat_input:
            self.dynmat_input[item] = dynmat_input[item]

    def dynmat(self, directory="tmp-qe-static", inpname="dynmat-gamma.in", output="dynmat-gamma.out", runopt="gen", auto=0):
        """
        the default output file name of dynamt.x is dynmat.out
        so we should not redirect the output of running of dynmat.x(not output file of dynamt.x)
        to dynamt.out to save us from leaving it a mess.
        """
        # first check whether there is a previous scf running
        if not os.path.exists(directory):
            print("===================================================\n")
            print("                 Warning !!!\n")
            print("===================================================\n")
            print("dynmat.x calculation:\n")
            print("  directory of previous scf or nscf calculattion not found!\n")
            sys.exit(1)
        if runopt == "gen" or runopt == "genrun":
            with open(os.path.join(directory, inpname), 'w') as fout:
                fout.write("&input\n")
                for item in self.dynmat_input:
                    if self.dynmat_input[item] is not None:
                        if type(self.dynmat_input[item]) == str:
                            fout.write("%s = '%s'\n" % (item, self.dynmat_input[item]))
                        else:
                            fout.write("%s = %s\n" % (item, self.dynmat_input[item]))
                fout.write("/\n")
                fout.write("\n")

            # gen yhbatch script
            self.gen_yh(directory=directory, inpname=inpname, output=output, cmd="dynmat.x")
            # gen pbs script
            self.gen_pbs(directory=directory, inpname=inpname, output=output, cmd="dynmat.x", jobname=self.run_params["jobname"], nodes=self.run_params["nodes"], ppn=self.run_params["ppn"])

        if runopt == "run" or runopt == "genrun":
            os.chdir(directory)
            os.system("%s dynmat.x < %s | tee %s" % (self.run_params["mpi"], inpname, output))
            os.chdir("../")
        server_handle(auto=auto, directory=directory, jobfilebase="dynmat-gamma", server=self.run_params["server"])

    def ir_raman(self, directory="tmp-qe-static", mpi="", runopt="gen"):
        """
        Reference:
            https://larrucea.eu/compute-ir-raman-spectra-qe/

        General procedure of calculation IR and Raman using ph.x mainly
            1. Optimize the wavefunction by performing an Self Consistent Field (scf) calculation with pw.x
            2. Calculate the vibrational frequencies (normal modes/phonons) with ph.x
            3. Extract the phonon information from ph.x output using dynmat.x
            4. Parse the dynmat.x output section that contains the spectra data (frequencies and intensities) and plot it with gnuplot, producing these two spectra:
        """
        self.phx(mpi=mpi, runopt=runopt)
        self.dynmat(mpi=mpi, runopt=runopt)

    #
    def gen_yh(self, inpname, output, directory="tmp-qe-static", cmd="ph.x"):
        """
        generating yhbatch job script for calculation
        """
        with open(os.path.join(directory, inpname.split(".in")[0]+".sub"), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("yhrun -N 1 -n 24 %s < %s > %s\n" % (cmd, inpname, output))

    def gen_pbs(self, inpname, output, directory, cmd, jobname, nodes=1, ppn=32):
        """
        generating pbs job script for calculation
        """
        with open(os.path.join(directory, inpname.split(".in")[0]+".pbs"), 'w') as fout:
            fout.write("#!/bin/bash\n")
            fout.write("#PBS -N %s\n" % jobname)
            fout.write("#PBS -l nodes=%d:ppn=%d\n" % (nodes, ppn))
            fout.write("cd $PBS_O_WORKDIR\n")
            fout.write("NP=`cat $PBS_NODEFILE | wc -l`\n")
            fout.write("\n")
            fout.write("mpirun -np $NP -machinefile $PBS_NODEFILE %s < %s > %s\n" % (cmd, inpname, output))
