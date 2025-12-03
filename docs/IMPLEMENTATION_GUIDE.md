# Customer Journey as Code - Implementation Guide

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Graph Schema](#graph-schema)
3. [Atom Structure](#atom-structure)
4. [Creating Your First Journey](#creating-your-first-journey)
5. [Advanced Patterns](#advanced-patterns)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Core Concepts

### The Atomic Hierarchy

```
Journey (30+ days)
  └── Phase (7-14 days)
        └── Module (2-5 days)
              └── Atom (hours to 2 days)
```

### Atom Types

1. **Customer Actions**
   - Front-stage touchpoints
   - Customer-visible
   - Examples: Upload documents, e-sign forms, review disclosures

2. **Back-Office Actions**
   - Back-stage operations
   - Internal processing
   - Examples: Review documents, calculate income, underwrite loan

3. **System Actions**
   - Automated processes
   - System integrations
   - Examples: Submit to AUS, generate disclosure, send notification

### Front-Stage vs Back-Stage

| Front-Stage | Back-Stage |
|-------------|------------|
| Customer sees/experiences | Customer doesn't see |
| Portal interactions | Internal systems |
| Notifications | Processing workflows |
| Decision communications | Calculations |
| Customer effort required | Staff effort required |

## Graph Schema

### Node Types

#### 1. Atom Node
```json
{
  "id": "atom-cust-upload-paystubs",
  "type": "atom",
  "title": "Customer Uploads Pay Stubs",
  "actor": "customer",
  "atom_type": "customer-action",
  "customer_visible": true,
  "front_stage": true,
  "sla_hours": 24,
  "regulatory_refs": ["ECOA", "ATR/QM"],
  "description": "Customer uploads most recent 2 pay stubs"
}
```

**Required Fields:**
- `id`: Unique identifier (format: `atom-{actor_prefix}-{description}`)
- `type`: Always "atom"
- `title`: Human-readable title
- `actor`: Who performs the action
- `atom_type`: customer-action | back-office-action | system-action
- `customer_visible`: boolean
- `front_stage`: boolean
- `sla_hours`: Number (decimal allowed)

**Optional Fields:**
- `regulatory_refs`: Array of strings
- `description`: String
- `risk_category`: low | medium | high | critical

#### 2. Module Node
```json
{
  "id": "module-asset-verification",
  "type": "module",
  "title": "Asset Verification Workflow",
  "description": "Complete workflow for verifying borrower assets",
  "sla_hours": 48,
  "atoms": [
    "atom-cust-upload-bank-statements",
    "atom-bo-review-assets",
    "atom-bo-calculate-reserves"
  ]
}
```

#### 3. Phase Node
```json
{
  "id": "phase-underwriting",
  "type": "phase",
  "title": "Underwriting Phase",
  "description": "Comprehensive loan underwriting",
  "sla_hours": 120,
  "modules": [
    "module-income-verification",
    "module-asset-verification",
    "module-credit-review"
  ]
}
```

#### 4. Journey Node
```json
{
  "id": "journey-fha-purchase",
  "type": "journey",
  "title": "FHA Purchase Loan Journey",
  "description": "Complete customer journey for FHA purchase",
  "loan_type": "FHA",
  "transaction_type": "purchase",
  "sla_days": 30,
  "phases": [
    "phase-application",
    "phase-processing",
    "phase-underwriting",
    "phase-closing"
  ]
}
```

### Edge Types

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| `enables` | Prerequisites | Application enables document upload |
| `triggers` | Cause-effect | Document upload triggers review |
| `sequential` | Ordered steps | Review before calculation |
| `data-flows-to` | Data dependency | Calculation feeds underwriting |
| `contains` | Hierarchical | Module contains atoms |

Example:
```json
{
  "source": "atom-cust-upload-w2",
  "target": "atom-bo-review-income",
  "type": "triggers"
}
```

## Atom Structure

### YAML Template

```yaml
---
id: atom-[actor]-[description]
type: atom
title: Human Readable Title
version: 1.0.0

# Classification
atom_type: customer-action | back-office-action | system-action
actor: customer | processor | underwriter | system | loan_officer | closer
front_stage: true | false
customer_visible: true | false

# Timing
sla_hours: 24
criticality: low | medium | high | critical

# Description
description: |
  Detailed description of what happens in this touchpoint.
  Multiple lines supported.

# Pre-conditions (what must be true before this atom can execute)
preconditions:
  - Customer has created account
  - Documents are ready
  - System is operational

# Steps (the actual process)
steps:
  - step: 1
    action: Description of step 1
    system: "System name if applicable"
  - step: 2
    action: Description of step 2
    regulatory: "Regulation if applicable"

# Post-conditions (what becomes true after execution)
postconditions:
  - Documents stored in DMS
  - Notification sent
  - Workflow advanced

# Data Generated
data_outputs:
  - Document IDs
  - Timestamps
  - Validation results

# Regulatory & Compliance
regulatory_refs:
  - TRID
  - ECOA
  - ATR/QM

risk_category: medium
compliance_notes: |
  Important compliance considerations.

# Customer Experience (for customer-facing atoms)
customer_sentiment_impact: positive | neutral | negative
customer_effort_score: low | medium | high
touchpoint_importance: low | medium | high | critical

pain_points:
  - Finding documents
  - Scanning quality

# Dependencies
depends_on:
  - atom-id-1
enables:
  - atom-id-2
triggers:
  - atom-id-3

# Metrics
success_metrics:
  - Completion rate > 90%
  - Average time < 10 minutes

# Notes
notes: |
  Additional context, optimization opportunities, etc.
```

## Creating Your First Journey

### Step 1: Plan Your Journey

1. **Identify the Journey**
   - Loan type (Conventional, FHA, VA)
   - Transaction type (Purchase, Refinance)
   - Target timeline

2. **Define Phases**
   - Application
   - Processing
   - Underwriting
   - Closing

3. **Identify Modules per Phase**
   - Income verification
   - Asset verification
   - Credit review
   - Appraisal
   - Title work

4. **List Atoms per Module**
   - Customer actions
   - Processor actions
   - Underwriter actions
   - System actions

### Step 2: Create Atoms

Use the atom generator:

```bash
# Customer actions
npm run generate "Customer uploads bank statements"
npm run generate "Customer e-signs initial disclosures"

# Processor actions
npm run generate "Processor orders credit report"
npm run generate "Processor calculates debt-to-income ratio"

# System actions
npm run generate "System generates Loan Estimate"
npm run generate "System submits to Desktop Underwriter"
```

Edit generated YAML files to add:
- Detailed descriptions
- Step-by-step procedures
- Regulatory references
- Success metrics

### Step 3: Build the Graph

Edit `graph/customer-journey-graph.json`:

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "created": "2025-12-03",
    "description": "Your journey description"
  },
  "nodes": {
    // Add your atoms
    "atom-cust-upload-statements": { ... },

    // Add modules
    "module-asset-verification": {
      "id": "module-asset-verification",
      "type": "module",
      "title": "Asset Verification",
      "atoms": [
        "atom-cust-upload-statements",
        "atom-bo-review-assets"
      ]
    },

    // Add phases
    "phase-processing": {
      "id": "phase-processing",
      "type": "phase",
      "title": "Processing Phase",
      "modules": ["module-asset-verification"]
    },

    // Add journey
    "journey-your-journey": {
      "id": "journey-your-journey",
      "type": "journey",
      "title": "Your Journey Name",
      "phases": ["phase-processing"]
    }
  },
  "edges": [
    {
      "source": "atom-cust-upload-statements",
      "target": "atom-bo-review-assets",
      "type": "triggers"
    }
  ]
}
```

### Step 4: Validate

```bash
npm run validate
```

Fix any errors reported:
- Broken references
- Missing required fields
- Circular dependencies

### Step 5: Build & Visualize

```bash
# Build documentation
npm run build

# View generated docs
ls dist/journeys/

# Start visualization server
npm start
# Open http://localhost:3000/customer-journey/public/journey-graph-viewer.html
```

## Advanced Patterns

### Pattern 1: Conditional Branches

For journeys with decision points:

```json
{
  "nodes": {
    "atom-bo-initial-review": { ... },
    "atom-bo-request-more-docs": { ... },
    "atom-bo-proceed-to-underwriting": { ... }
  },
  "edges": [
    {
      "source": "atom-bo-initial-review",
      "target": "atom-bo-request-more-docs",
      "type": "triggers",
      "condition": "incomplete"
    },
    {
      "source": "atom-bo-initial-review",
      "target": "atom-bo-proceed-to-underwriting",
      "type": "triggers",
      "condition": "complete"
    }
  ]
}
```

### Pattern 2: Parallel Workflows

For operations that can happen concurrently:

```json
{
  "nodes": {
    "atom-trigger-parallel": { ... },
    "atom-parallel-1": { ... },
    "atom-parallel-2": { ... },
    "atom-join": { ... }
  },
  "edges": [
    { "source": "atom-trigger-parallel", "target": "atom-parallel-1", "type": "triggers" },
    { "source": "atom-trigger-parallel", "target": "atom-parallel-2", "type": "triggers" },
    { "source": "atom-parallel-1", "target": "atom-join", "type": "sequential" },
    { "source": "atom-parallel-2", "target": "atom-join", "type": "sequential" }
  ]
}
```

### Pattern 3: Reusable Atoms

Same atom used in multiple modules:

```json
{
  "nodes": {
    "atom-sys-credit-pull": { ... },
    "module-initial-review": {
      "atoms": ["atom-sys-credit-pull", ...]
    },
    "module-final-review": {
      "atoms": ["atom-sys-credit-pull", ...]
    }
  }
}
```

## Best Practices

### Naming Conventions

1. **Atom IDs**: `atom-{actor}-{action}-{object}`
   - ✅ `atom-cust-upload-w2`
   - ✅ `atom-bo-calculate-dti`
   - ✅ `atom-sys-generate-le`
   - ❌ `uploadW2` (no prefix, unclear)

2. **Module IDs**: `module-{workflow-name}`
   - ✅ `module-income-verification`
   - ✅ `module-title-review`

3. **Phase IDs**: `phase-{stage-name}`
   - ✅ `phase-underwriting`
   - ✅ `phase-closing`

4. **Journey IDs**: `journey-{loantype}-{transaction}`
   - ✅ `journey-conventional-purchase`
   - ✅ `journey-fha-refinance`

### SLA Guidelines

- **Customer Actions**: 24-48 hours (allow time for gathering docs)
- **Quick Processor Tasks**: 2-8 hours
- **In-depth Reviews**: 8-24 hours
- **Underwriting**: 24-72 hours
- **System Actions**: Minutes (0.25-0.5 hours)

### Regulatory Mapping

Always include for customer-facing touchpoints:

- **TRID**: Application, disclosures, waiting periods
- **ECOA**: Credit decisions, adverse action
- **ATR/QM**: Income verification, DTI calculation
- **FCRA**: Credit report usage
- **RESPA**: Settlement services, affiliated business

## Troubleshooting

### Validation Errors

**Error**: "Edge references non-existent target"
- **Fix**: Ensure atom/module/phase IDs in edges match node IDs exactly

**Error**: "Module SLA doesn't match sum of atoms"
- **Fix**: Recalculate module SLA as sum of contained atom SLAs

**Error**: "Circular dependency detected"
- **Fix**: Remove circular edges - journeys should be DAGs (Directed Acyclic Graphs)

### Build Errors

**Error**: "Cannot read YAML component"
- **Fix**: Verify YAML syntax, ensure file has `.yaml` extension

**Error**: "Component not found"
- **Fix**: Ensure atom YAML files are in correct subdirectory

### Visualization Issues

**Issue**: Nodes overlap
- **Fix**: Adjust force simulation parameters in `journey-graph-viewer.html`

**Issue**: Too many nodes to see clearly
- **Fix**: Use zoom controls, or create separate graphs per phase

## Scaling to 100+ Atoms

### Organization Strategy

```
journey-components/
├── atoms/
│   ├── customer-actions/
│   │   ├── application/
│   │   ├── documentation/
│   │   └── closing/
│   ├── back-office-actions/
│   │   ├── processing/
│   │   ├── underwriting/
│   │   └── closing/
│   └── system-actions/
│       ├── disclosures/
│       ├── aus/
│       └── notifications/
```

### Graph Management

For large graphs, consider splitting:

1. **master-graph.json**: All nodes and edges
2. **conventional-purchase.json**: Subset for one journey
3. **fha-purchase.json**: Subset for another journey

Build process can merge subgraphs.

### Performance Optimization

- Use pagination in visualization (show 50 nodes at a time)
- Implement graph filters (by actor, by phase, by loan type)
- Cache built documentation
- Use incremental builds (only rebuild changed journeys)

---

**Questions?** Open an issue or consult the main README.md
