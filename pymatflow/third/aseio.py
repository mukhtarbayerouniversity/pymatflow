"""
converting between other structure file and xyz format(with second line specifying
the cell parameter), with the help of ase.io
"""
import ase.io
import pymatflow.base as base


def read_cif(filepath):
    """
    :param filepath filepath of the cif file
    :return cell and atoms need to build the pymatflow.structure.crystal object
    """
    a = ase.io.read(filepath, format='cif')
    cell = a.cell.tolist()
    atoms = []
    for i in range(len(a.arrays['numbers'])):
        for item in base.element:
            if base.element[item].number == a.arrays['numbers'][i]:
                symbol = item
                break
        atoms.append(base.Atom(
            symbol,
            a.arrays['positions'][i, 0],
            a.arrays['positions'][i, 1],
            a.arrays['positions'][i, 2]
            ))
    return cell, atoms

def write_cif(cell, atoms, filepath):
    """
    :param cell: cell of the structure
    :param atoms: atoms of the structure
    :param filepath: the output cif file path
    """
    from ase import Atoms
    numbers = []
    positions = []
    for atom in atoms:
        numbers.append(base.element[atom.name].number)
        positions.append([atom.x, atom.y, atom.z])
    a = Atoms(numbers=numbers, cell=cell, positions=positions)
    ase.io.write(filepath, a, format='cif')


def read_xtd(filepath):
    """
    :param filepath filepath of the xtd file
    :return cell and atoms need to build the pymatflow.structure.crystal object
    """
    a = ase.io.read(filepath, format='xtd')
    cell = a.cell.tolist()
    atoms = []
    for i in range(len(a.arrays['numbers'])):
        for item in base.element:
            if base.element[item].number == a.arrays['numbers'][i]:
                symbol = item
                break
        atoms.append(base.Atom(
            symbol,
            a.arrays['positions'][i, 0],
            a.arrays['positions'][i, 1],
            a.arrays['positions'][i, 2]
            ))
    return cell, atoms

def write_xtd(cell, atoms, filepath):
    """
    :param cell: cell of the structure
    :param atoms: atoms of the structure
    :param filepath: the output xtd file path
    """
    from ase import Atoms
    numbers = []
    positions = []
    for atom in atoms:
        numbers.append(base.element[atom.name].number)
        positions.append([atom.x, atom.y, atom.z])
    a = Atoms(numbers=numbers, cell=cell, positions=positions)
    ase.io.write(filepath, a, format='xtd')
