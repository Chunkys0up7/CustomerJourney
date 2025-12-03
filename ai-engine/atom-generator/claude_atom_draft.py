#!/usr/bin/env python3
"""
Claude-Powered Atom Generator
Converts SOPs or process documentation into Customer Journey Atoms

Usage:
    python claude_atom_draft.py <sop_file_path> [output_dir]

Example:
    python claude_atom_draft.py ../../docs/SOP-Income-Verification.md ../../journey-components/atoms/candidate/

Requirements:
    pip install anthropic pyyaml
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
import sys
import yaml
import anthropic
from pathlib import Path
from datetime import datetime

# Claude Model Configuration
MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4000

# Atom Generation Prompt Template
ATOM_GENERATION_PROMPT = """You are an expert in mortgage origination processes and customer journey mapping.

I will provide you with a Standard Operating Procedure (SOP) or process documentation. Your task is to:

1. **Identify Atomic Steps**: Break down the SOP into indivisible atoms (smallest meaningful units)
2. **Classify Each Atom**: Determine if it's:
   - front_stage (customer-facing)
   - back_stage (back-office operation)
   - system (automated integration)
3. **Map to Taxonomy**:
   - Front-stage: information_submission, decision_point, acknowledgment, communication_receipt, waiting_state
   - Back-stage: data_validation, document_review, calculation, decision, external_request, compliance_check, handoff
   - System: api_call, data_transform, queue_management, timer_event

4. **Identify Dependencies**: What must happen before/after each atom?
5. **Extract Regulatory Requirements**: TRID, RESPA, ECOA, FCRA, HMDA, etc.
6. **Estimate Timing**: Duration and SLAs

Generate atoms in YAML format following this schema:

```yaml
id: atom-{type}-{seq}-{short-name}
name: Human Readable Name
category: [see taxonomy above]
stage: front_stage | back_stage | system
actor: borrower | loan_officer | processor | underwriter | closer | system
channel: web | mobile | email | phone | in_person | api
description: |
  Detailed description of what happens in this atom

estimated_duration_minutes: [number]
sla_hours: [number, for back_stage only]
sla_unit: business_days | hours

dependencies:
  requires: [list of atom_ids]
  enables: [list of atom_ids]
  parallel_with: [list of atom_ids]

data_inputs:
  - field: [field_name]
    source: [atom_id or 'external']
    required: [true/false]
    format: [string/number/date/etc]

data_outputs:
  - field: [field_name]
    destination: [atom_id or 'storage']
    format: [string/number/etc]

regulatory_requirements:
  - regulation: [TRID/RESPA/ECOA/etc]
    section: [regulation section]
    description: [what's required]
    deadline_days: [number]

# For front_stage atoms:
customer_experience:
  effort_level: low | medium | high
  emotional_impact: negative | neutral | positive
  nps_impact: -10 to +10
  pain_points: [list]
  delight_opportunities: [list]

# For back_stage atoms:
process_metrics:
  automation_level: manual | semi_automated | automated
  error_rate_percent: [number]
  rework_rate_percent: [number]
  bottleneck_risk: low | medium | high
  staffing_fte: [number]

# For system atoms:
system_integration:
  system_name: [name]
  api_endpoint: [url, if applicable]
  authentication: oauth2 | api_key | basic_auth
  timeout_seconds: [number]
  retry_policy: none | exponential_backoff | fixed_interval
  max_retries: [number]

version: "1.0.0"
last_updated: [ISO8601 timestamp]
change_log:
  - version: "1.0.0"
    date: [ISO8601]
    author: "AI Generator"
    description: "Initial atom creation from SOP"
    breaking_changes: false

tags: [relevant, tags]
notes: [any implementation notes]
```

**IMPORTANT**:
- Generate ONLY complete, valid YAML
- Use proper YAML syntax (no tabs, proper indentation)
- Provide realistic estimates based on mortgage industry standards
- Include all required fields
- One atom per response

Here is the SOP/documentation to analyze:

--- SOP CONTENT ---
{sop_content}
--- END SOP ---

Generate the first atom from this SOP. If this SOP contains multiple atoms, focus on the first logical step.
"""


class ClaudeAtomGenerator:
    """Generate atoms from SOPs using Claude API"""

    def __init__(self, api_key=None):
        """Initialize Claude client"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def read_sop(self, filepath):
        """Read SOP file content"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_atom(self, sop_content, iteration=1):
        """
        Generate a single atom from SOP content using Claude

        Args:
            sop_content: Full SOP text
            iteration: Which atom in sequence (for multi-atom SOPs)

        Returns:
            dict: Parsed atom definition
        """
        prompt = ATOM_GENERATION_PROMPT.format(sop_content=sop_content)

        if iteration > 1:
            prompt += f"\n\nThis is iteration {iteration}. Generate the NEXT atom in sequence."

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response text
            response_text = message.content[0].text

            # Parse YAML from response
            # Handle markdown code blocks if present
            if "```yaml" in response_text:
                yaml_start = response_text.find("```yaml") + 7
                yaml_end = response_text.find("```", yaml_start)
                yaml_text = response_text[yaml_start:yaml_end].strip()
            elif "```" in response_text:
                yaml_start = response_text.find("```") + 3
                yaml_end = response_text.find("```", yaml_start)
                yaml_text = response_text[yaml_start:yaml_end].strip()
            else:
                yaml_text = response_text

            # Parse YAML
            atom = yaml.safe_load(yaml_text)

            # Validate required fields
            required_fields = ['id', 'name', 'category', 'stage', 'actor', 'version']
            for field in required_fields:
                if field not in atom:
                    raise ValueError(f"Missing required field: {field}")

            return atom

        except anthropic.APIError as e:
            print(f"❌ Claude API Error: {e}")
            return None
        except yaml.YAMLError as e:
            print(f"❌ YAML Parsing Error: {e}")
            print(f"Response was:\n{response_text}")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return None

    def save_atom(self, atom, output_dir):
        """Save atom to YAML file in appropriate subfolder"""
        output_path = Path(output_dir)

        # Determine subfolder based on stage
        if atom['stage'] == 'front_stage':
            subfolder = 'customer-actions'
        elif atom['stage'] == 'back_stage':
            subfolder = 'back-office-actions'
        else:
            subfolder = 'system-actions'

        # Create full output directory
        full_dir = output_path / subfolder
        full_dir.mkdir(parents=True, exist_ok=True)

        # Write file
        filepath = full_dir / f"{atom['id']}.yaml"
        with open(filepath, 'w') as f:
            yaml.dump(atom, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return str(filepath)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python claude_atom_draft.py <sop_file_path> [output_dir]")
        print("\nExample:")
        print("  python claude_atom_draft.py ../../docs/SOP-Income-Verification.md ../../journey-components/atoms/candidate/")
        sys.exit(1)

    sop_filepath = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../../journey-components/atoms/candidate"

    if not os.path.exists(sop_filepath):
        print(f"❌ Error: SOP file not found: {sop_filepath}")
        sys.exit(1)

    print(f"🤖 Claude Atom Generator")
    print(f"{'=' * 60}")
    print(f"📄 SOP File: {sop_filepath}")
    print(f"📁 Output Dir: {output_dir}")
    print(f"🧠 Model: {MODEL}")
    print(f"{'=' * 60}\n")

    # Initialize generator
    try:
        generator = ClaudeAtomGenerator()
    except ValueError as e:
        print(f"❌ {e}")
        print("\nPlease set your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Read SOP
    print("📖 Reading SOP...")
    sop_content = generator.read_sop(sop_filepath)
    print(f"   SOP length: {len(sop_content)} characters\n")

    # Generate atoms (allow multiple iterations)
    atoms_generated = []
    max_iterations = 5  # Prevent infinite loops

    for i in range(1, max_iterations + 1):
        print(f"🔬 Generating Atom {i}...")

        atom = generator.generate_atom(sop_content, iteration=i)

        if atom:
            # Save atom
            filepath = generator.save_atom(atom, output_dir)
            atoms_generated.append(filepath)

            print(f"✅ Generated: {atom['id']}")
            print(f"   Name: {atom['name']}")
            print(f"   Stage: {atom['stage']}")
            print(f"   Category: {atom['category']}")
            print(f"   File: {filepath}\n")

            # Ask if user wants to generate more
            if i < max_iterations:
                response = input("Generate another atom from this SOP? (y/N): ").strip().lower()
                if response != 'y':
                    break
        else:
            print(f"❌ Failed to generate atom {i}\n")
            break

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ Complete! Generated {len(atoms_generated)} atom(s)")
    print(f"{'=' * 60}")

    for filepath in atoms_generated:
        print(f"  - {filepath}")

    print(f"\nNext steps:")
    print(f"1. Review generated atoms for accuracy")
    print(f"2. Validate with: python ../../tools/validate.py {output_dir}")
    print(f"3. Move from 'candidate/' to appropriate atoms/ subfolder")
    print(f"4. Update dependencies between atoms")


if __name__ == "__main__":
    main()
