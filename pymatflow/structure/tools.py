"""
providing tools for structure manipulation
"""

import sys
import copy
import numpy as np


def move_along(structure, atoms_to_move, direc, disp):
    """
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    :params atoms_to_move: a list of atoms to move, counting starts with 0
    :param direc: three number to indicate the direction to move along
        namely the crystal orientation index
    :param disp: displacement of the atoms in unit of Angstrom
    """
    # do some checking
    if max(atoms_to_move) > (len(structure.atoms) - 1):
        print("=============================================================================\n")
        print("                              WARNING \n")
        print("------------------------------------------------------------------------------\n")
        print("the atom you are trying to move is beyond the number of atoms in the structure\n")
        sys.exit(1)

    direc_cartesian = np.array(structure.cell[0]) * direc[0] + np.array(structure.cell[1]) * direc[1] + np.array(structure.cell[2]) * direc[2]
    # normalize
    length = np.sqrt(direc_cartesian[0]**2+direc_cartesian[1]**2+direc_cartesian[2]**2)
    direc_cartesian = direc_cartesian / length

    deltax = direc_cartesian[0] * disp
    deltay = direc_cartesian[1] * disp
    deltaz = direc_cartesian[2] * disp

    for i in atoms_to_move:
        structure.atoms[i].x += deltax
        structure.atoms[i].y += deltay
        structure.atoms[i].z += deltaz
    # end

def remove_atoms(structure, atoms_to_remove):
    """
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    :params atoms_to_remove: a list of atoms to remove, counting starts with 0
    """
    # do some checking
    if max(atoms_to_remove) > (len(structure.atoms) - 1):
        print("=============================================================================\n")
        print("                              WARNING \n")
        print("------------------------------------------------------------------------------\n")
        print("the atom you are trying to remove is beyond the number of atoms in the structure\n")
        sys.exit(1)

    for i in atoms_to_remove:
        structure.atoms[i] = None
    while None in structure.atoms:
        structure.atoms.remove(None)
    # end    

def vacuum_layer(structure, plane, thickness):
    """
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    :param plane: the plane chosen to add vacuum layer, can be:
        1 -> ab plane
        2 -> ac plane
        3 -> bc plane
    :param thickness: thickness of the vacuum layer
    """
    if plane == 1:
        ab = np.cross(structure.cell[0], structure.cell[1])
        # get the cos of the angle between c and outer product of ab
        cos_angle = np.dot(structure.cell[2], ab) / (np.linalg.norm(structure.cell[2]), np.linalg.norm(ab))
        scale_c = (thickness + np.linalg.norm(structure.cell[2])) / np.linalg.norm(structure.cell[2])
        for i in range(3):
            structure.cell[2][i] *= scale_c
    elif plane == 2:
        ac = np.cross(structure.cell[0], structure.cell[2])
        # get the cos of the angle between c and outer product of ab
        cos_angle = np.dot(structure.cell[1], ac) / (np.linalg.norm(structure.cell[1]), np.linalg.norm(ac))
        scale_b = (thickness + np.linalg.norm(structure.cell[1])) / np.linalg.norm(structure.cell[1])
        for i in range(3):
            structure.cell[1][i] *= scale_b            
    elif plane == 3:
        bc = np.cross(structure.cell[1], structure.cell[2])
        # get the cos of the angle between c and outer product of ab
        cos_angle = np.dot(structure.cell[0], bc) / (np.linalg.norm(structure.cell[0]), np.linalg.norm(bc))
        scale_a = (thickness + np.linalg.norm(structure.cell[0])) / np.linalg.norm(structure.cell[0])
        for i in range(3):
            structure.cell[0][i] *= scale_a
    else:
        pass
    # end

    
def inverse_geo_center(structure):
    """
    calc the geometric center of the system and make an inversion against that center
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    """
    # calc the geometric center
    x = 0
    y = 0
    z = 0
    for atom in structure.atoms:
        x += atom.x
        y += atom.y
        z += atom.z
    x /= len(structure.atoms)
    y /= len(structure.atoms)
    z /= len(structure.atoms)
    # now get the symmetry image against the geometric center
    for atom in structure.atoms:
        atom.x = x * 2 - atom.x
        atom.y = y * 2 - atom.y
        atom.z = z * 2 - atom.z
    # end

def inverse_point(structure, point):
    """
    calc the geometric center of the system and make an inversion against that center
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    :param point: the inverse center point, like [0.0, 0.0, 0.0]
    """
    # now get the symmetry image against the inverse center
    for atom in structure.atoms:
        atom.x = point[0] * 2 - atom.x
        atom.y = point[1] * 2 - atom.y
        atom.z = point[2] * 2 - atom.z
    # end

def inverse_cell_center(structure):
    """
    make an inversion against the cell center
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    """
    # first transfer to fractional coordinate and inverse against [0.5, 0.5, 0.5]
    structure.natom = len(structure.atoms)
    frac = structure.get_fractional()
    for atom in frac:
        atom[1] = 0.5 * 2 - atom[1]
        atom[2] = 0.5 * 2 - atom[2]
        atom[3] = 0.5 * 2 - atom[3]
    # convert frac to cartesian again
    latcell = np.array(structure.cell)
    convmat = latcell.T
    from pymatflow.base.atom import Atom
    structure.atoms = []
    for atom in frac:
        cartesian = list(convmat.dot(np.array([atom[1], atom[2], atom[3]])))
        structure.atoms.append(Atom(name=atom[0], x=cartesian[0], y=cartesian[1], z=cartesian[2]))
    #

def rotate_along_axis(structure, rotate_atoms=[], axis=[]):
    """
    rotate the specified atoms along the specified axis
    :param structure: an instance of pymatflow.structure.crystal.crystal()
    """
    pass
    
    
def enlarge_atoms(structure):
    """
    :return out:
        atoms: [
                ["C", 0.00000, 0.000000, 0.0000],
                ["O", 0.00000, 0.500000, 0.0000],
                ...
            ]
    Note: will enlarge the atoms in the unit cell along both a, b, c and -a, -b, -c direction.
        but the cell is not redefined, the returned atoms is not used to form crystal, but to be 
        tailored by redefine_lattice function to get atoms for the redfined lattice.
        The goal is to make sure when the cell rotate in the 3D space, it will always be filled
        with atoms.
    """
    from pymatflow.base.atom import Atom
    #
    cell = copy.deepcopy(structure.cell)
    a = np.linalg.norm(cell[0])
    b = np.linalg.norm(cell[1])
    c = np.linalg.norm(cell[2])
    
    n1 = np.ceil(np.max([a, b, c]) / a ) * 2 # maybe times 2 is not needed
    n2 = np.ceil(np.max([a, b, c]) / b ) * 2
    n3 = np.ceil(np.max([a, b, c]) / c ) * 2
    n = [int(n1), int(n2), int(n3)]
    
    atoms = copy.deepcopy(structure.atoms)
    # build supercell: replica in three vector one by one
    for i in range(3):
        natom_now = len(atoms)
        for j in range(n[i] - 1):
            for atom in atoms[:natom_now]:
                x = atom.x + float(j + 1) * structure.cell[i][0]
                y = atom.y + float(j + 1) * structure.cell[i][1]
                z = atom.z + float(j + 1) * structure.cell[i][2]
                atoms.append(Atom(atom.name, x, y, z))
        # replicate in the negative direction of structure.cell[i]
        for atom in atoms[:natom_now*n[i]]:
            x = atom.x - float(n[i]) * structure.cell[i][0]
            y = atom.y - float(n[i]) * structure.cell[i][1]
            z = atom.z - float(n[i]) * structure.cell[i][2]
            atoms.append(Atom(atom.name, x, y, z))
    return [[atom.name, atom.x, atom.y, atom.z] for atom in atoms]

def redefine_lattice(structure, a, b, c):
    """
    :param a, b, c: new lattice vectors in terms of old.
        new_a = a[0] * old_a + a[1] * old_b + a[2] * old_c
        like a=[1, 0, 0], b=[0, 1, 0], c=[0, 0, 1] actually defines the
        same lattice as old.
    :return an object of crystal()
    Method:
        first make a large enough supercell, which guarantee that all the atoms in the new lattice are inside
        the supercell.
        then redfine the cell, and calc the fractional coord of all atoms with regarding the new cell
        finally remove those atoms who's fractional coord is not within range [0, 1], and we can convert fractional
        coords to cartesian.
    """
    from pymatflow.structure.crystal import crystal
    from pymatflow.base.atom import Atom
    old_cell = copy.deepcopy(structure.cell)
    new_cell = copy.deepcopy(structure.cell)
    new_cell[0] = list(a[0] * np.array(old_cell[0]) + a[1] * np.array(old_cell[1]) + a[2] * np.array(old_cell[2]))
    new_cell[1] = list(b[0] * np.array(old_cell[0]) + b[1] * np.array(old_cell[1]) + b[2] * np.array(old_cell[2]))
    new_cell[2] = list(c[0] * np.array(old_cell[0]) + c[1] * np.array(old_cell[1]) + c[2] * np.array(old_cell[2]))
    
    
    # enlarge the system
    atoms_container = crystal()
    atoms_container.get_atoms(enlarge_atoms(structure=structure))
    
    # now calc the fractional coordinates of all atoms in atoms_container with new_cell as reference
    atoms_frac = []
    latcell_new = np.array(new_cell)
    convmat_new = np.linalg.inv(latcell_new.T)
    for i in range(len(atoms_container.atoms)):
        atom = []
        atom.append(atoms_container.atoms[i].name)
        atom = atom + list(convmat_new.dot(np.array([atoms_container.atoms[i].x, atoms_container.atoms[i].y, atoms_container.atoms[i].z])))
        atoms_frac.append(atom)
    
    atoms_frac_within_new_cell = []
    for atom in atoms_frac:
        if 0 <= atom[1] < 1 and 0 <= atom[2] < 1 and 0 <= atom[3] < 1:
            atoms_frac_within_new_cell.append(atom)
            
    # now convert coord of atom in atoms_frac_within_new_cell to cartesian
    out = crystal()
    out.atoms = []
    latcell_new = np.array(new_cell)
    convmat_frac_to_cartesian = latcell_new.T
    for atom in atoms_frac_within_new_cell:
        cartesian = list(convmat_frac_to_cartesian.dot(np.array([atom[1], atom[2], atom[3]])))
        out.atoms.append(Atom(name=atom[0], x=cartesian[0], y=cartesian[1], z=cartesian[2]))
    #
    
    out.cell = new_cell
    
    return out