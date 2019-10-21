#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from setuptools import setup, find_packages
from setuptools import Command
import os

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name = "emuhelper",
    version = '0.1',
    keywords = ("Emulation, DFT"),
    description = "an emulation assistant",
    license = "",
    url = "",
    author_email = "emulab@163.com",
    packages = find_packages(),
    #data_files = [('noteseton/uis', ['noteseton/uis/app.ui', 'noteseton/uis/menubar.ui', 'noteseton/uis/appmenu.ui'])],
    include_package_data = True,
    platforms = "any",
    install_requires = ["pymatgen"],

    scripts = [
        "emuhelper/abinit/scripts/bands_abinit.py",
        "emuhelper/abinit/scripts/converge_ecut_abinit.py",
        "emuhelper/abinit/scripts/dos_abinit.py",
        "emuhelper/abinit/scripts/geo_opt_abinit.py",
        "emuhelper/abinit/scripts/md_abinit.py",
        "emuhelper/abinit/scripts/neb_abinit.py",
        "emuhelper/abinit/scripts/phonon_abinit.py",
        "emuhelper/abinit/scripts/phonon_with_phonopy_abinit.py",
        "emuhelper/abinit/scripts/abinit-md.py",
        "emuhelper/abinit/scripts/abinit-opt.py",
        "emuhelper/abinit/scripts/abinit-single-point.py",
        "emuhelper/abinit/scripts/abinit-converge-ecut.py",
        "emuhelper/abinit/scripts/abinit-dos.py",
        "emuhelper/abinit/scripts/abinit-bands.py",
        "emuhelper/abinit/scripts/abinit-phonopy.py",
        "emuhelper/abinit/scripts/abinit-berry-phase.py",
        "emuhelper/abinit/scripts/abinit-dft-u.py",
        "emuhelper/cp2k/scripts/cp2k-aimd.py",
        "emuhelper/cp2k/scripts/bands_cp2k.py",
        "emuhelper/cp2k/scripts/converge_cutoff_cp2k.py",
        "emuhelper/cp2k/scripts/cp2k-converge-cutoff.py",
        "emuhelper/cp2k/scripts/converge_rel_cutoff_cp2k.py",
        "emuhelper/cp2k/scripts/cp2k-converge-rel-cutoff.py",
        "emuhelper/cp2k/scripts/electron_density_cp2k.py",
        "emuhelper/cp2k/scripts/geo_opt_cp2k.py",
        "emuhelper/cp2k/scripts/mp2_cp2k.py",
        "emuhelper/cp2k/scripts/pdos_cp2k.py",
        "emuhelper/cp2k/scripts/phonon_cp2k.py",
        "emuhelper/cp2k/scripts/single-point-cp2k.py",
        "emuhelper/cp2k/scripts/cp2k-geo-opt.py",
        "emuhelper/cp2k/scripts/cp2k-cell-opt.py",
        "emuhelper/cp2k/scripts/cp2k-scf.py",
        "emuhelper/cp2k/scripts/cp2k-scf-restart.py",
        "emuhelper/cp2k/scripts/cp2k-vib.py",
        "emuhelper/cp2k/post/scripts/post-single-point-cp2k.py",
        "emuhelper/cp2k/post/scripts/post-geo-opt-cp2k.py",
        "emuhelper/cp2k/post/scripts/post-pdos-without-convolute.py",
        "emuhelper/cp2k/post/scripts/post-cp2k-geo-opt.py",
        "emuhelper/cp2k/post/scripts/post-cp2k-cell-opt.py",
        "emuhelper/cp2k/post/scripts/post-cp2k-scf.py",
        "emuhelper/cp2k/post/scripts/post-cp2k-pdos.py",
        "emuhelper/dalton/single_point_dalton.py",
        "emuhelper/orca/single_point_orca.py",
        "emuhelper/orca/geo_opt_orca.py",
        "emuhelper/orca/converge_multiplicity_orca.py",
        "emuhelper/qe/scripts/converge_ecutrho_pwscf.py",
        "emuhelper/qe/scripts/converge_ecutwfc_pwscf.py",
        "emuhelper/qe/scripts/geo_opt_not_vc_pwscf.py",
        "emuhelper/qe/scripts/geo_opt_vc_pwscf.py",
        "emuhelper/qe/scripts/phonon_with_phonopy_pwscf.py",
        "emuhelper/qe/scripts/phonon_with_phx_pwscf.py",
        "emuhelper/qe/scripts/converge-ecutwfc-pwscf.py",
        "emuhelper/qe/scripts/qe-opt.py",
        "emuhelper/qe/scripts/qe-md.py",
        "emuhelper/qe/scripts/qe-vc-md.py",
        "emuhelper/qe/scripts/qe-converge-ecutwfc.py",
        "emuhelper/qe/scripts/qe-converge-ecutrho.py",
        "emuhelper/qe/scripts/qe-converge-kpoints.py",
        "emuhelper/qe/scripts/qe-converge-degauss.py",
        "emuhelper/qe/scripts/qe-scf-nscf.py",
        "emuhelper/qe/scripts/qe-scf-nscf-dos.py",
        "emuhelper/qe/scripts/qe-scf-nscf-bands.py",
        "emuhelper/qe/scripts/qe-nscf.py",
        "emuhelper/qe/scripts/qe-scf.py",
        "emuhelper/qe/scripts/qe-dos.py",
        "emuhelper/qe/scripts/qe-bands.py",
        "emuhelper/qe/scripts/qe-pdos.py",
        "emuhelper/qe/scripts/qe-epsilon.py",
        "emuhelper/qe/scripts/qe-ir-raman.py",
        "emuhelper/qe/scripts/qe-elf.py",
        "emuhelper/qe/scripts/qe-fermi-surface.py",
        "emuhelper/qe/scripts/qe-dcd.py",
        "emuhelper/qe/scripts/qe-ed.py",
        "emuhelper/qe/scripts/qe-relax.py",
        "emuhelper/qe/scripts/qe-vc-relax.py",
        "emuhelper/qe/scripts/qe-neb.py",
        "emuhelper/qe/scripts/qe-turbo-davidson-spectrum.py",
        "emuhelper/qe/scripts/qe-turbo-lanczos-spectrum.py",
        "emuhelper/qe/scripts/qe-phx.py",
        "emuhelper/qe/post/scripts/post-qe-dos.py",
        "emuhelper/qe/post/scripts/post-qe-pdos.py",
        "emuhelper/qe/post/scripts/post-qe-neb.py",
        "emuhelper/qe/post/scripts/post-qe-relax.py",
        "emuhelper/qe/post/scripts/post-qe-vc-relax.py",
        "emuhelper/qe/post/scripts/post-qe-scf.py",
        "emuhelper/siesta/scripts/band_new_scf_siesta.py",
        "emuhelper/siesta/scripts/charge-density_potentials_siesta.py",
        "emuhelper/siesta/scripts/chem_analysis_siesta.py",
        "emuhelper/siesta/scripts/converge_ecut_siesta.py",
        "emuhelper/siesta/scripts/coord_from_xyz_to_siesta.py",
        "emuhelper/siesta/scripts/dos-pdos_new_scf_siesta.py",
        "emuhelper/siesta/scripts/siesta-pdos.py",
        "emuhelper/siesta/scripts/geo_opt_siesta.py",
        "emuhelper/siesta/scripts/siesta-opt.py",
        "emuhelper/siesta/scripts/ldos_new_scf_siesta.py",
        "emuhelper/siesta/scripts/macro_polarization_siesta.py",
        "emuhelper/siesta/scripts/md_siesta.py",
        "emuhelper/siesta/scripts/siesta-md.py",
        "emuhelper/siesta/scripts/net-charge_dipole_elec-field_siesta.py",
        "emuhelper/siesta/scripts/optical_siesta.py",
        "emuhelper/siesta/scripts/phonon_siesta.py",
        "emuhelper/siesta/scripts/phonon_with_phonopy_siesta.py",
        "emuhelper/siesta/scripts/wannier90_siesta.py",
        "emuhelper/siesta/scripts/xyz2fdf.py",
        "emuhelper/siesta/scripts/siesta-converge-cutoff.py",
        "emuhelper/siesta/scripts/siesta-scf.py",
        "emuhelper/siesta/scripts/siesta-scf-restart.py",
        "emuhelper/siesta/post/scripts/post-siesta-pdos.py",
        "emuhelper/tools/build_supercell.py",
        "emuhelper/tools/cluster_sphere.py"
        ],
    #entry_points = {
    #    'console_scripts': [
    #        'noteseton = main:main'
    #    ]
    #},

    cmdclass = {
        'clean': CleanCommand,
    }
)



