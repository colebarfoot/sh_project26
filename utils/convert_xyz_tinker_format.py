import numpy as np
import os
import shutil

# Create the 'output' folder if it doesn't exist
output_folder = "$HOME/src/sh-project/water_data/output"
os.makedirs(output_folder, exist_ok=True)

def read_xyz(input_file_name):
    with open(input_file_name, 'r') as file:
        lines = file.readlines()

    atom_data = [line.strip().split() for line in lines[2:]]
    atom_coords = np.array([[float(x) for x in line[1:]] for line in atom_data if len(line) > 1])
    atom_labels = np.array([line[0] for line in atom_data if len(line) > 1])

    return atom_labels, atom_coords

def assign_molecules(atom_labels, atom_coords):
    carbon_indices = np.where(atom_labels == 'O')[0]
    hydrogen_indices = np.where(atom_labels == 'H')[0]
    hydrogen_coords = atom_coords[hydrogen_indices]

    molecule_id = 1
    molecule_assignments = np.zeros(len(atom_labels), dtype=int)
    bonds = []
    angles = []

    for idx in carbon_indices:
        carbon_coord = atom_coords[idx]
        distances = np.linalg.norm(hydrogen_coords - carbon_coord, axis=1)
        bonded_h_indices = hydrogen_indices[distances < 1.0]

        if len(bonded_h_indices) == 2:
            molecule_assignments[idx] = molecule_id
            molecule_assignments[bonded_h_indices] = molecule_id
            for h_idx in bonded_h_indices:
                bonds.append((idx, h_idx))
            for i in range(len(bonded_h_indices)):
                for j in range(i + 1, len(bonded_h_indices)):
                    angles.append((bonded_h_indices[i], idx, bonded_h_indices[j]))
            molecule_id += 1

    return molecule_assignments, bonds, angles

def write_lammps_data(output_file_name, atom_labels, atom_coords, molecule_assignments, bonds, angles):
    # ====== FIX THIS !!!! =======
    atom_types = {'O': 1, 'H': 2}
    bond_coeff = [1, 1.09, 340.00, -500.0, 700.0]  # Adjusted bond coefficients
    angle_coeff = [1, 0, 1, 109.5, 62.0, -30.0, 10.0, -5.0, 7.0]  # Adjusted angle coefficients

    # Filter out atoms not part of any methane molecule
    valid_indices = molecule_assignments > 0
    atom_labels = atom_labels[valid_indices]
    atom_coords = atom_coords[valid_indices]
    molecule_assignments = molecule_assignments[valid_indices]

    # Update bonds and angles to reflect filtered atom indices
    atom_index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(np.where(valid_indices)[0])}
    bonds = [(atom_index_map[bond[0]], atom_index_map[bond[1]]) for bond in bonds if bond[0] in atom_index_map and bond[1] in atom_index_map]
    angles = [(atom_index_map[angle[0]], atom_index_map[angle[1]], atom_index_map[angle[2]]) for angle in angles if angle[0] in atom_index_map and angle[1] in atom_index_map and angle[2] in atom_index_map]

    with open(output_file_name, 'w') as file:
        num_atoms = len(atom_labels)
        num_bonds = len(bonds)
        num_angles = len(angles)
        num_atom_types = len(set(atom_labels))
        num_bond_types = 1
        num_angle_types = 1

        file.write("LAMMPS Description\n\n")
        file.write(f"{num_atoms} atoms\n")
        file.write(f"{num_bonds} bonds\n")
        file.write(f"{num_angles} angles\n")
        file.write(f"{num_atom_types} atom types\n")
        file.write(f"{num_bond_types} bond types\n")
        file.write(f"{num_angle_types} angle types\n\n")
        
        file.write(f"{atom_coords[:,0].min() - 1} {atom_coords[:,0].max() + 1} xlo xhi\n")
        file.write(f"{atom_coords[:,1].min() - 1} {atom_coords[:,1].max() + 1} ylo yhi\n")
        file.write(f"{atom_coords[:,2].min() - 1} {atom_coords[:,2].max() + 1} zlo zhi\n\n")

        # Writing the Masses section
        file.write("Masses\n\n")
        file.write("1 15.999  # Carbon mass\n")
        file.write("2 1.008   # Hydrogen mass\n\n")

        file.write("Atoms # atomic\n\n")
        for i, (label, coord, mol_id) in enumerate(zip(atom_labels, atom_coords, molecule_assignments), start=1):
            type_id = atom_types[label]
            charge = 0  # Zero column as placeholder
            x, y, z = coord
            file.write(f"{i} {mol_id} {type_id} {charge} {x:.5f} {y:.5f} {z:.5f}\n")

        file.write("\nBonds\n\n")
        for i, (atom1, atom2) in enumerate(bonds, start=1):
            file.write(f"{i} 1 {atom1 + 1} {atom2 + 1}\n")

        file.write("\nAngles\n\n")
        for i, angle in enumerate(angles, start=1):
            h1, c, h2 = [x + 1 for x in angle]
            file.write(f"{i} 1 {h1} {c} {h2}\n")
        
        # Writing the Coefficients sections
        file.write("\nBond Coeffs\n\n")
        
        file.write(f"{bond_coeff[0]} {bond_coeff[1]} {bond_coeff[2]} {bond_coeff[3]} {bond_coeff[4]}\n\n")
        
        file.write("Angle Coeffs\n\n")
        
        file.write(f"{angle_coeff[0]} {angle_coeff[1]} {angle_coeff[2]} {angle_coeff[3]} {angle_coeff[4]} {angle_coeff[5]} {angle_coeff[6]} {angle_coeff[7]} {angle_coeff[8]}\n\n")

        file.write("BondAngle Coeffs\n\n")
        
        file.write("1 0.0 0.0 0.0 0.0\n\n")  # Placeholder values
        
        file.write("UreyBradley Coeffs\n\n")
        
        file.write("1 0.0 0.0\n\n")  # Placeholder values

        file.write("Tinker Types\n\n")
        for i, label in enumerate(atom_labels, start=1):
            tinker_type = 1 if label == 'C' else 2
            file.write(f"{i} {tinker_type}\n")


# List of .xyz files and corresponding output file names
xyz_files = [
    "ice_viii.xyz"
]




# Loop through each file and process it
for xyz_file in xyz_files:
    # Derive the output file name
    output_file = xyz_file.replace('.xyz', '.lmp')
    
    # Read the .xyz file and process
    atom_labels, atom_coords = read_xyz(xyz_file)
    molecule_assignments, bonds, angles = assign_molecules(atom_labels, atom_coords)
    
    # Write the LAMMPS data file
    write_lammps_data(output_file, atom_labels, atom_coords, molecule_assignments, bonds, angles)
    
    # Move the .lmp file to the 'output' folder
    shutil.move(output_file, os.path.join(output_folder, os.path.basename(output_file)))

print("Conversion complete for all files.")

