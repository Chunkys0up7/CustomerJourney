#!/usr/bin/env python3
"""
Export all atoms to JSON for dashboard consumption
"""

import yaml
import json
from pathlib import Path

def load_all_atoms():
    """Load all atom YAML files"""
    atoms = []
    atom_dirs = [
        "journey-components/atoms/customer-actions",
        "journey-components/atoms/back-office-actions",
        "journey-components/atoms/system-actions"
    ]

    for dir_path in atom_dirs:
        atom_dir = Path(dir_path)
        if not atom_dir.exists():
            continue

        for yaml_file in atom_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    atom = yaml.safe_load(f)
                    if atom and 'id' in atom:
                        # Simplify atom for dashboard (remove heavy fields)
                        simple_atom = {
                            "id": atom.get("id"),
                            "name": atom.get("name"),
                            "stage": atom.get("stage"),
                            "phase": atom.get("phase"),
                            "category": atom.get("category"),
                            "actor": atom.get("actor"),
                            "channel": atom.get("channel", "web"),
                            "estimated_duration_minutes": atom.get("estimated_duration_minutes", 0),
                            "sla_hours": atom.get("sla_hours"),
                            "dependencies": atom.get("dependencies", {}),
                            "regulatory_requirements": atom.get("regulatory_requirements", []),
                            "customer_experience": atom.get("customer_experience", {}),
                            "process_metrics": atom.get("process_metrics", {}),
                            "data_outputs": atom.get("data_outputs", [])
                        }
                        atoms.append(simple_atom)
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")

    return atoms

def main():
    """Export atoms to JSON"""
    print("📦 Exporting atoms to JSON...")

    atoms = load_all_atoms()
    print(f"   Loaded {len(atoms)} atoms")

    # Create output directory
    output_dir = Path("public/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON file
    output_file = output_dir / "atoms.json"
    with open(output_file, 'w') as f:
        json.dump({
            "atoms": atoms,
            "generated_at": "2024-01-15T00:00:00Z",
            "version": "1.0.0",
            "total_count": len(atoms)
        }, f, indent=2)

    print(f"✅ Exported to {output_file}")

    # Stats by phase
    phases = {}
    for atom in atoms:
        phase = atom.get("phase", "Unknown")
        if phase not in phases:
            phases[phase] = {"front": 0, "back": 0, "system": 0}

        stage = atom.get("stage")
        if stage == "front_stage":
            phases[phase]["front"] += 1
        elif stage == "back_stage":
            phases[phase]["back"] += 1
        else:
            phases[phase]["system"] += 1

    print("\n📊 Atoms by Phase:")
    for phase, counts in sorted(phases.items()):
        total = counts["front"] + counts["back"] + counts["system"]
        print(f"   {phase}: {total} atoms (Front: {counts['front']}, Back: {counts['back']}, System: {counts['system']})")

if __name__ == "__main__":
    main()
