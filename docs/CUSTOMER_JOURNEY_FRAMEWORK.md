# Customer Journey as Code Framework
**NASA-STD-2100-91 Inspired Atomic Documentation for Mortgage Origination**

## Table of Contents
1. [Overview](#overview)
2. [Atomic Taxonomy](#atomic-taxonomy)
3. [Atom Schema](#atom-schema)
4. [Module Composition](#module-composition)
5. [Phase Orchestration](#phase-orchestration)
6. [Impact Analysis Framework](#impact-analysis-framework)
7. [Integration with SOPs](#integration-with-sops)
8. [Regulatory Mapping](#regulatory-mapping)

---

## Overview

This framework applies NASA-STD-2100-91 atomic documentation principles to customer journey mapping in mortgage origination. Just as NASA's Data Item Descriptions (DIDs) provide reusable, composable documentation templates, our **Customer Journey Atoms** represent indivisible units of customer experience and business process.

### Core Principles

| NASA Principle | Customer Journey Application |
|---------------|------------------------------|
| **Atoms** (indivisible units) | Single customer action or back-office step |
| **DIDs** (template modules) | Reusable workflow patterns (Income Verification, Appraisal) |
| **Type (d) Pointers** | Dependencies between atoms without duplication |
| **Type (f) Rollouts** | Phases containing multiple modules |
| **Tailoring Checklist** | Loan type variants (FHA, VA, Self-Employed) |
| **Impact Analysis** | Change propagation before process updates |

---

## Atomic Taxonomy

### 1. Front-Stage Atoms (Customer-Facing)
Atoms where customers directly interact with the mortgage process.

**Categories:**
- `information_submission` - Customer provides data
- `decision_point` - Customer makes a choice
- `acknowledgment` - Customer receives and acknowledges information
- `communication_receipt` - Customer receives updates
- `waiting_state` - Customer is idle while back-office works

**Attributes:**
- `customer_effort_level`: low | medium | high
- `emotional_impact`: negative | neutral | positive
- `channel`: web | mobile | email | phone | in-person
- `estimated_duration_minutes`: number

**Examples:**
- `atom-cust-01-inquiry` - Initial loan inquiry
- `atom-cust-02-consent-credit` - Credit authorization
- `atom-cust-03-app-submit` - Application submission
- `atom-cust-04-doc-upload` - Document upload

---

### 2. Back-Stage Atoms (Back-Office)
Internal operations invisible to customers but critical to journey progression.

**Categories:**
- `data_validation` - Verify information accuracy
- `document_review` - Manual review of submissions
- `calculation` - Numerical processing (DTI, LTV, etc.)
- `decision` - Underwriting or approval decision
- `external_request` - Third-party service call
- `compliance_check` - Regulatory validation
- `handoff` - Transfer between teams/systems

**Attributes:**
- `owner_role`: loan_officer | processor | underwriter | closer
- `sla_hours`: number (business hours)
- `automation_level`: manual | semi-automated | automated
- `regulatory_requirements`: [TRID, RESPA, ECOA, etc.]

**Examples:**
- `atom-bo-01-assign-lo` - Loan officer assignment
- `atom-bo-02-preq-calc` - Pre-qualification calculation
- `atom-bo-03-income-validation` - Income verification
- `atom-bo-04-appraisal-order` - Appraisal ordering

---

### 3. System Atoms (Integration)
Automated system actions connecting front and back stages.

**Categories:**
- `api_call` - External service integration
- `data_transform` - Data format conversion
- `queue_management` - Task routing
- `timer_event` - Scheduled or triggered action

**Attributes:**
- `system_name`: string (LOS, AUS, Credit Bureau, etc.)
- `api_endpoint`: URL
- `timeout_seconds`: number
- `retry_policy`: none | exponential_backoff | fixed_interval

**Examples:**
- `atom-sys-01-soft-credit` - Soft credit pull
- `atom-sys-02-aus-submit` - AUS submission
- `atom-sys-03-email-preq` - Pre-qual letter email
- `atom-sys-04-voe-request` - Automated VOE request

---

## Atom Schema

### Full YAML Schema

```yaml
id: string                          # atom-{type}-{seq}-{short-name}
name: string                        # Human-readable name
category: enum                      # See taxonomy above
stage: front_stage | back_stage | system

# Actor & Channel
actor: borrower | loan_officer | processor | underwriter | closer | system
channel: web | mobile | email | phone | in-person | api

# Timing & SLA
estimated_duration_minutes: number
sla_hours: number                   # Business hours for back-stage atoms
sla_unit: business_days | calendar_days

# Dependencies
dependencies:
  requires: [atom_id]               # Must complete before this atom
  enables: [atom_id]                # This atom unlocks these atoms
  parallel_with: [atom_id]          # Can run concurrently

# Data
data_inputs:
  - field: string
    source: atom_id | external
    required: boolean

data_outputs:
  - field: string
    destination: atom_id | storage
    format: string

# Regulatory
regulatory_requirements:
  - regulation: TRID | RESPA | ECOA | FCRA | HMDA
    section: string
    description: string

# Experience Metrics (front-stage only)
customer_experience:
  effort_level: low | medium | high
  emotional_impact: negative | neutral | positive
  nps_impact: -10 to +10

# Process Metrics (back-stage only)
process_metrics:
  automation_level: manual | semi_automated | automated
  error_rate_percent: number
  rework_rate_percent: number

# SOP Links
sop_links:
  - sop_id: string
    relevance: primary | supporting
    section: string

# Versioning
version: semver
last_updated: ISO8601
change_log:
  - version: string
    date: ISO8601
    description: string
```

---

## Module Composition

**Modules** are reusable workflow patterns composed of multiple atoms. They represent complete sub-processes.

### Example: Income Verification Module

```yaml
id: module-income-verification
name: Income Verification
description: Complete workflow for verifying borrower employment and income

owner_role: processor
target_hours: 24
customer_milestone: Income Verified

atoms:
  - atom-cust-05-income-w2-upload
  - atom-sys-04-voe-request
  - atom-bo-05-income-calculation
  - atom-bo-06-income-review
  - atom-cust-06-income-clarification
  - atom-bo-07-income-approval

success_criteria:
  - All income sources documented
  - VOE received for W2 employees
  - YTD income matches application
  - 2-year history verified

failure_modes:
  - VOE not returned within 5 days
  - Income discrepancy > 10%
  - Self-employment requires CPA letter
```

### Standard Modules

| Module ID | Name | Atoms | Target Hours | Milestone |
|-----------|------|-------|--------------|-----------|
| `module-pre-qualification` | Pre-Qualification | 7 | 1 | Pre-Approved |
| `module-income-verification` | Income Verification | 6 | 24 | Income Verified |
| `module-asset-verification` | Asset Verification | 5 | 48 | Assets Verified |
| `module-appraisal` | Appraisal Process | 8 | 120 | Appraisal Complete |
| `module-aus-processing` | AUS Submission | 4 | 2 | AUS Approved |
| `module-underwriting` | Underwriting Review | 10 | 72 | Clear to Close |
| `module-closing-prep` | Closing Preparation | 8 | 48 | CD Issued |
| `module-funding` | Loan Funding | 6 | 24 | Loan Funded |

---

## Phase Orchestration

**Phases** are major journey stages containing multiple modules. They represent customer-visible milestones.

### 9-Phase Purchase Journey

```
1. Pre-Qualification
   └─ module-pre-qualification

2. Application
   └─ module-application-intake

3. Disclosure
   └─ module-initial-disclosure

4. Processing
   ├─ module-income-verification
   ├─ module-asset-verification
   ├─ module-appraisal
   └─ module-title-insurance

5. Underwriting
   ├─ module-aus-processing
   └─ module-underwriting

6. Clear to Close
   └─ module-ctc-validation

7. Closing Disclosure
   └─ module-closing-prep

8. Closing
   └─ module-closing-execution

9. Funding
   └─ module-funding
```

### Phase Schema

```yaml
id: string
name: string
description: string
modules: [module_id]
customer_milestone: string
typical_duration_days: number
regulatory_deadlines:
  - event: string
    deadline_days: number
    regulation: string
```

---

## Impact Analysis Framework

### Change Propagation Algorithm

When an atom changes (timing, requirements, outputs), propagate impact downstream:

```python
def analyze_impact(changed_atom_id):
    """
    Traverse dependency graph to identify all affected atoms.
    """
    affected = {
        'immediate': [],      # Direct dependencies
        'downstream': [],     # Transitive dependencies
        'customer_facing': [], # Customer experience impact
        'regulatory': [],     # Compliance risk
        'sla_cascade': []     # Timing impacts
    }

    # 1. Find immediate dependencies
    for atom in all_atoms:
        if changed_atom_id in atom.dependencies.requires:
            affected['immediate'].append(atom.id)

    # 2. Traverse downstream (recursive)
    queue = affected['immediate'].copy()
    while queue:
        current = queue.pop(0)
        for atom in all_atoms:
            if current in atom.dependencies.requires:
                if atom.id not in affected['downstream']:
                    affected['downstream'].append(atom.id)
                    queue.append(atom.id)

    # 3. Categorize customer vs back-office
    all_affected = affected['immediate'] + affected['downstream']
    for atom_id in all_affected:
        atom = get_atom(atom_id)
        if atom.stage == 'front_stage':
            affected['customer_facing'].append(atom_id)

    # 4. Check regulatory requirements
    changed_atom = get_atom(changed_atom_id)
    if changed_atom.regulatory_requirements:
        affected['regulatory'] = changed_atom.regulatory_requirements

    # 5. Calculate SLA cascade
    for atom_id in all_affected:
        atom = get_atom(atom_id)
        if atom.sla_hours:
            affected['sla_cascade'].append({
                'atom_id': atom_id,
                'current_sla': atom.sla_hours,
                'risk': 'high' if atom.customer_experience.effort_level == 'high' else 'medium'
            })

    return affected
```

### Impact Report Template

```markdown
# Impact Analysis Report
**Changed Atom:** atom-bo-05-income-validation
**Change Type:** SLA increase (24h → 48h)
**Date:** 2024-01-15

## Immediate Impact
- atom-bo-06-income-review (depends on income-validation)
- atom-cust-06-income-clarification (may be delayed)

## Downstream Impact (5 atoms affected)
- module-income-verification: +24h overall
- phase-processing: +24h overall
- Customer milestone "Income Verified": Delayed 1 day

## Customer Experience
- **Effort Level:** No change
- **Communication:** Add status update at 36h mark
- **NPS Risk:** Medium (longer wait time)

## Regulatory Risk
- **TRID:** No impact (income verification not on critical path for LE)
- **ECOA:** Ensure timely adverse action notice if income insufficient

## Recommendations
1. Add automated status email at 36h
2. Update customer portal ETA messaging
3. Review processor workload capacity
4. Consider parallel appraisal ordering to offset delay
```

---

## Integration with SOPs

Each atom links to relevant Standard Operating Procedures (SOPs) from your SOPDemo repository.

### SOP Link Schema

```yaml
sop_links:
  - sop_id: sop-mf-009-appraisal-review
    relevance: primary          # This SOP defines this atom
    section: "3.2 Quality Check"

  - sop_id: sop-mf-005-wire-transfer-security
    relevance: supporting       # This SOP provides context
    section: "2.1 Verification"
```

### Bidirectional Impact Analysis

**SOP → Journey:** When an SOP changes, identify affected atoms
```bash
python tools/sop-impact.py sop-mf-009-appraisal-review modify
```

**Journey → SOP:** When an atom changes, identify affected SOPs
```bash
python tools/atom-impact.py atom-bo-uw-appraisal-review modify
```

---

## Regulatory Mapping

### Key Regulations

| Regulation | Atoms Affected | Key Requirements |
|------------|----------------|------------------|
| **TRID** | 12 atoms | 3-day LE, 7-day waiting, 3-day CD |
| **RESPA** | 8 atoms | Affiliated business disclosures, settlement services |
| **ECOA** | 6 atoms | Adverse action timing, fair lending |
| **FCRA** | 4 atoms | Credit pull authorization, dispute resolution |
| **HMDA** | 3 atoms | Data collection, reporting requirements |

### Regulatory Atom Tags

```yaml
# Example: Application Submission Atom
regulatory_requirements:
  - regulation: TRID
    section: "12 CFR 1026.19(e)"
    description: "Triggers 3-business-day waiting period for LE"
    deadline_days: 3

  - regulation: ECOA
    section: "12 CFR 1002.9(a)(1)"
    description: "Start 30-day adverse action clock"
    deadline_days: 30
```

---

## Next Steps

1. **Generate Atoms**: Use AI atom generator to draft atoms from existing SOPs
   ```bash
   python ai-engine/atom-generator/claude_atom_draft.py docs/SOP-Income-Verification.md
   ```

2. **Validate**: Check atom compliance with schema
   ```bash
   python tools/validate.py atoms/
   ```

3. **Compose Modules**: Build modules from validated atoms
   ```bash
   python tools/compose-module.py module-income-verification.yaml
   ```

4. **Analyze Impact**: Before making changes, run impact analysis
   ```bash
   python tools/impact-analyzer.py atom-bo-05-income-validation modify
   ```

5. **Visualize**: View journey graph with front/back stage mapping
   ```bash
   npm start
   # Open http://localhost:3000/public/journey-graph-viewer.html
   ```

---

## Version History

- **v1.0.0** (2024-01-15): Initial framework release
  - Atomic taxonomy (front/back/system)
  - Complete atom schema
  - Module composition patterns
  - 9-phase purchase journey
  - Impact analysis framework
  - SOP integration model
