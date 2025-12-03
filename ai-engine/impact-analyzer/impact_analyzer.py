#!/usr/bin/env python3
"""
Customer Journey Impact Analyzer
Analyzes the downstream impact of changes to atoms or modules

Usage:
    python impact_analyzer.py <atom_id> <change_type> [--report-format=markdown|json]

Example:
    python impact_analyzer.py atom-bo-005-income-validation modify --report-format=markdown

Change Types:
    - modify: Changing timing, requirements, or outputs
    - remove: Removing an atom
    - add: Adding a new atom
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from collections import deque
from typing import Dict, List, Set, Tuple

class ImpactAnalyzer:
    """Analyze impact of changes to customer journey atoms"""

    def __init__(self, atoms_dir="../../journey-components/atoms"):
        """Initialize analyzer by loading all atoms"""
        self.atoms_dir = Path(atoms_dir)
        self.atoms = {}
        self.dependency_graph = {}
        self.reverse_dependency_graph = {}

        self._load_all_atoms()
        self._build_dependency_graph()

    def _load_all_atoms(self):
        """Load all atom YAML files"""
        for yaml_file in self.atoms_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    atom = yaml.safe_load(f)
                    if atom and 'id' in atom:
                        self.atoms[atom['id']] = atom
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")

        print(f"✅ Loaded {len(self.atoms)} atoms")

    def _build_dependency_graph(self):
        """Build forward and reverse dependency graphs"""
        for atom_id, atom in self.atoms.items():
            # Forward dependencies (what this atom enables)
            enables = atom.get('dependencies', {}).get('enables', [])
            self.dependency_graph[atom_id] = enables

            # Reverse dependencies (what requires this atom)
            requires = atom.get('dependencies', {}).get('requires', [])
            for req_atom_id in requires:
                if req_atom_id not in self.reverse_dependency_graph:
                    self.reverse_dependency_graph[req_atom_id] = []
                self.reverse_dependency_graph[req_atom_id].append(atom_id)

    def analyze_impact(self, atom_id: str, change_type: str) -> Dict:
        """
        Analyze impact of changing an atom

        Args:
            atom_id: ID of atom being changed
            change_type: 'modify', 'remove', or 'add'

        Returns:
            Dict with impact analysis results
        """
        if atom_id not in self.atoms:
            return {"error": f"Atom not found: {atom_id}"}

        changed_atom = self.atoms[atom_id]

        impact = {
            "changed_atom": {
                "id": atom_id,
                "name": changed_atom.get('name'),
                "stage": changed_atom.get('stage'),
                "category": changed_atom.get('category')
            },
            "change_type": change_type,
            "timestamp": datetime.now().isoformat(),
            "immediate_impact": [],
            "downstream_impact": [],
            "customer_facing_impact": [],
            "regulatory_impact": [],
            "sla_cascade": [],
            "affected_modules": [],
            "risk_assessment": {}
        }

        # Find immediate dependencies
        immediate = self.reverse_dependency_graph.get(atom_id, [])
        impact["immediate_impact"] = [
            {
                "atom_id": aid,
                "name": self.atoms[aid].get('name'),
                "stage": self.atoms[aid].get('stage')
            }
            for aid in immediate if aid in self.atoms
        ]

        # Find downstream dependencies (BFS traversal)
        downstream = self._find_downstream(atom_id)
        impact["downstream_impact"] = [
            {
                "atom_id": aid,
                "name": self.atoms[aid].get('name'),
                "stage": self.atoms[aid].get('stage'),
                "distance": dist
            }
            for aid, dist in downstream
        ]

        # Identify customer-facing impact
        all_affected = [atom_id] + immediate + [aid for aid, _ in downstream]
        for aid in all_affected:
            if aid in self.atoms and self.atoms[aid].get('stage') == 'front_stage':
                atom = self.atoms[aid]
                impact["customer_facing_impact"].append({
                    "atom_id": aid,
                    "name": atom.get('name'),
                    "customer_experience": atom.get('customer_experience', {}),
                    "estimated_duration_minutes": atom.get('estimated_duration_minutes')
                })

        # Check regulatory impact
        reqs = changed_atom.get('regulatory_requirements', [])
        if reqs:
            impact["regulatory_impact"] = [
                {
                    "regulation": req.get('regulation'),
                    "section": req.get('section'),
                    "description": req.get('description'),
                    "deadline_days": req.get('deadline_days')
                }
                for req in reqs
            ]

        # Calculate SLA cascade
        for aid in all_affected:
            if aid in self.atoms:
                atom = self.atoms[aid]
                sla = atom.get('sla_hours')
                if sla:
                    impact["sla_cascade"].append({
                        "atom_id": aid,
                        "name": atom.get('name'),
                        "current_sla_hours": sla,
                        "risk": self._assess_sla_risk(atom)
                    })

        # Risk assessment
        impact["risk_assessment"] = self._assess_risk(
            changed_atom,
            len(immediate),
            len(downstream),
            len(impact["customer_facing_impact"]),
            len(impact["regulatory_impact"])
        )

        return impact

    def _find_downstream(self, atom_id: str, max_depth=10) -> List[Tuple[str, int]]:
        """
        Find all downstream dependencies using BFS

        Returns:
            List of (atom_id, distance) tuples
        """
        visited = set()
        queue = deque([(atom_id, 0)])
        downstream = []

        while queue:
            current_id, depth = queue.popleft()

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Get atoms that depend on current
            dependents = self.reverse_dependency_graph.get(current_id, [])

            for dep_id in dependents:
                if dep_id not in visited and dep_id != atom_id:
                    downstream.append((dep_id, depth + 1))
                    queue.append((dep_id, depth + 1))

        return downstream

    def _assess_sla_risk(self, atom: Dict) -> str:
        """Assess SLA risk level"""
        sla = atom.get('sla_hours', 0)
        effort = atom.get('customer_experience', {}).get('effort_level')

        if sla < 4:
            return "high"
        elif sla < 24:
            return "medium"
        else:
            return "low"

    def _assess_risk(self, changed_atom, immediate_count, downstream_count,
                     customer_count, regulatory_count) -> Dict:
        """Assess overall risk of change"""
        risk_score = 0

        # Immediate dependencies add risk
        risk_score += immediate_count * 10

        # Downstream dependencies
        risk_score += downstream_count * 5

        # Customer-facing impact
        risk_score += customer_count * 15

        # Regulatory impact
        risk_score += regulatory_count * 20

        # Stage-specific risk
        if changed_atom.get('stage') == 'front_stage':
            risk_score += 10  # Customer-facing changes are risky

        # Determine risk level
        if risk_score < 30:
            level = "LOW"
            color = "🟢"
        elif risk_score < 70:
            level = "MEDIUM"
            color = "🟡"
        else:
            level = "HIGH"
            color = "🔴"

        return {
            "level": level,
            "score": risk_score,
            "color": color,
            "immediate_dependencies": immediate_count,
            "downstream_dependencies": downstream_count,
            "customer_facing_atoms": customer_count,
            "regulatory_requirements": regulatory_count
        }

    def generate_markdown_report(self, impact: Dict) -> str:
        """Generate markdown impact report"""
        if "error" in impact:
            return f"# Error\n\n{impact['error']}"

        risk = impact["risk_assessment"]
        changed = impact["changed_atom"]

        report = f"""# Impact Analysis Report

## Changed Atom
**ID:** `{changed['id']}`
**Name:** {changed['name']}
**Stage:** {changed['stage']}
**Category:** {changed['category']}
**Change Type:** {impact['change_type']}
**Analysis Date:** {impact['timestamp'][:10]}

---

## Risk Assessment

{risk['color']} **Risk Level: {risk['level']}** (Score: {risk['score']})

| Metric | Count |
|--------|-------|
| Immediate Dependencies | {risk['immediate_dependencies']} |
| Downstream Dependencies | {risk['downstream_dependencies']} |
| Customer-Facing Atoms | {risk['customer_facing_atoms']} |
| Regulatory Requirements | {risk['regulatory_requirements']} |

---

## Immediate Impact

Atoms that directly depend on this change:

"""

        if impact["immediate_impact"]:
            for atom in impact["immediate_impact"]:
                report += f"- `{atom['atom_id']}` - {atom['name']} ({atom['stage']})\n"
        else:
            report += "_No immediate dependencies_\n"

        report += "\n---\n\n## Downstream Impact\n\nAtoms affected through dependency chain:\n\n"

        if impact["downstream_impact"]:
            for atom in impact["downstream_impact"][:10]:  # Limit to 10
                report += f"- `{atom['atom_id']}` - {atom['name']} (distance: {atom['distance']})\n"

            if len(impact["downstream_impact"]) > 10:
                report += f"\n_...and {len(impact['downstream_impact']) - 10} more atoms_\n"
        else:
            report += "_No downstream dependencies_\n"

        report += "\n---\n\n## Customer Experience Impact\n\n"

        if impact["customer_facing_impact"]:
            for atom in impact["customer_facing_impact"]:
                cx = atom.get('customer_experience', {})
                effort = cx.get('effort_level', 'unknown')
                emotional = cx.get('emotional_impact', 'unknown')
                duration = atom.get('estimated_duration_minutes', '?')

                report += f"### {atom['name']}\n"
                report += f"- **Effort:** {effort}\n"
                report += f"- **Emotional Impact:** {emotional}\n"
                report += f"- **Duration:** {duration} minutes\n\n"
        else:
            report += "_No customer-facing impact_\n"

        report += "\n---\n\n## Regulatory Impact\n\n"

        if impact["regulatory_impact"]:
            for req in impact["regulatory_impact"]:
                report += f"### {req['regulation']}\n"
                report += f"**Section:** {req.get('section', 'N/A')}  \n"
                report += f"**Requirement:** {req.get('description', 'N/A')}  \n"
                report += f"**Deadline:** {req.get('deadline_days', '?')} days  \n\n"
        else:
            report += "_No regulatory impact identified_\n"

        report += "\n---\n\n## SLA Cascade\n\n"

        if impact["sla_cascade"]:
            for sla in impact["sla_cascade"]:
                risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(sla['risk'], "⚪")
                report += f"- {risk_emoji} `{sla['atom_id']}` - {sla['name']} ({sla['current_sla_hours']}h SLA)\n"
        else:
            report += "_No SLA impacts_\n"

        report += "\n---\n\n## Recommendations\n\n"

        # Generate recommendations based on risk level
        if risk['level'] == "HIGH":
            report += "⚠️ **HIGH RISK CHANGE**\n\n"
            report += "1. Conduct thorough testing of all affected atoms\n"
            report += "2. Review regulatory compliance for all affected requirements\n"
            report += "3. Update customer communication templates\n"
            report += "4. Schedule stakeholder review before implementation\n"
            report += "5. Plan phased rollout with monitoring\n"
        elif risk['level'] == "MEDIUM":
            report += "⚠️ **MEDIUM RISK CHANGE**\n\n"
            report += "1. Test affected downstream atoms\n"
            report += "2. Review customer-facing messaging\n"
            report += "3. Update any affected SOPs\n"
            report += "4. Monitor SLA performance after change\n"
        else:
            report += "✅ **LOW RISK CHANGE**\n\n"
            report += "1. Standard testing procedures\n"
            report += "2. Update documentation\n"
            report += "3. Monitor for unexpected impacts\n"

        return report

    def generate_json_report(self, impact: Dict) -> str:
        """Generate JSON impact report"""
        return json.dumps(impact, indent=2)


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python impact_analyzer.py <atom_id> <change_type> [--report-format=markdown|json]")
        print("\nChange Types: modify, remove, add")
        print("\nExample:")
        print("  python impact_analyzer.py atom-bo-005-income-validation modify")
        sys.exit(1)

    atom_id = sys.argv[1]
    change_type = sys.argv[2]
    report_format = "markdown"

    # Parse optional format flag
    if len(sys.argv) > 3 and sys.argv[3].startswith("--report-format="):
        report_format = sys.argv[3].split("=")[1]

    print(f"🔍 Customer Journey Impact Analyzer")
    print(f"{'=' * 60}")
    print(f"Atom: {atom_id}")
    print(f"Change Type: {change_type}")
    print(f"Report Format: {report_format}")
    print(f"{'=' * 60}\n")

    # Initialize analyzer
    analyzer = ImpactAnalyzer()

    # Analyze impact
    print(f"\n🔬 Analyzing impact...\n")
    impact = analyzer.analyze_impact(atom_id, change_type)

    # Generate report
    if report_format == "json":
        report = analyzer.generate_json_report(impact)
    else:
        report = analyzer.generate_markdown_report(impact)

    # Output report
    print(report)

    # Save to file
    output_filename = f"impact-report-{atom_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.{report_format if report_format == 'json' else 'md'}"
    with open(output_filename, 'w') as f:
        f.write(report)

    print(f"\n{'=' * 60}")
    print(f"📊 Report saved to: {output_filename}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
