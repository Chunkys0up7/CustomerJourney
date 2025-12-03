#!/usr/bin/env python3
"""
Batch Atom Generator
Generates a complete set of atoms for the mortgage purchase journey
"""

import yaml
import os
from datetime import datetime
from pathlib import Path

# Define all atoms for the complete purchase journey
ATOMS = [
    # === PHASE 1: PRE-QUALIFICATION ===
    {
        "id": "atom-cust-001-inquiry",
        "name": "Initial Loan Inquiry",
        "category": "information_submission",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower initiates loan inquiry through website or phone, providing basic property and financial information",
        "estimated_duration_minutes": 10,
        "customer_experience": {
            "effort_level": "low",
            "emotional_impact": "positive",
            "nps_impact": 5,
            "pain_points": [],
            "delight_opportunities": ["Quick response time", "Personalized greeting"]
        },
        "dependencies": {
            "requires": [],
            "enables": ["atom-cust-002-consent-credit", "atom-bo-001-assign-lo"]
        },
        "data_outputs": [
            {"field": "property_type", "destination": "storage", "format": "string"},
            {"field": "loan_amount", "destination": "storage", "format": "number"},
            {"field": "contact_info", "destination": "storage", "format": "object"}
        ]
    },
    {
        "id": "atom-cust-002-consent-credit",
        "name": "Credit Authorization Consent",
        "category": "acknowledgment",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower provides consent for soft credit pull and reviews FCRA disclosures",
        "estimated_duration_minutes": 5,
        "customer_experience": {
            "effort_level": "low",
            "emotional_impact": "neutral",
            "nps_impact": 0,
            "pain_points": ["Legal language complexity"],
            "delight_opportunities": ["Clear explanation of soft vs hard pull"]
        },
        "regulatory_requirements": [
            {
                "regulation": "FCRA",
                "section": "15 USC 1681",
                "description": "Requires borrower consent before credit pull",
                "deadline_days": 0
            }
        ],
        "dependencies": {
            "requires": ["atom-cust-001-inquiry"],
            "enables": ["atom-sys-001-soft-credit"]
        }
    },
    {
        "id": "atom-sys-001-soft-credit",
        "name": "Soft Credit Pull",
        "category": "api_call",
        "stage": "system",
        "actor": "system",
        "channel": "api",
        "description": "Automated soft credit inquiry to credit bureau (Experian, Equifax, or TransUnion)",
        "estimated_duration_minutes": 2,
        "system_integration": {
            "system_name": "Credit Bureau API",
            "authentication": "oauth2",
            "timeout_seconds": 30,
            "retry_policy": "exponential_backoff",
            "max_retries": 3
        },
        "dependencies": {
            "requires": ["atom-cust-002-consent-credit"],
            "enables": ["atom-bo-002-preq-calc"]
        }
    },
    {
        "id": "atom-bo-001-assign-lo",
        "name": "Loan Officer Assignment",
        "category": "handoff",
        "stage": "back_stage",
        "actor": "system",
        "channel": "api",
        "description": "System assigns loan officer based on availability, specialization, and workload",
        "estimated_duration_minutes": 1,
        "sla_hours": 1,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "automated",
            "error_rate_percent": 0.5,
            "rework_rate_percent": 1.0,
            "bottleneck_risk": "low"
        },
        "dependencies": {
            "requires": ["atom-cust-001-inquiry"],
            "enables": ["atom-bo-002-preq-calc"]
        }
    },
    {
        "id": "atom-bo-002-preq-calc",
        "name": "Pre-Qualification Calculation",
        "category": "calculation",
        "stage": "back_stage",
        "actor": "system",
        "channel": "api",
        "description": "Calculate maximum loan amount based on credit score, income, debts, and DTI ratios",
        "estimated_duration_minutes": 5,
        "sla_hours": 2,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "automated",
            "error_rate_percent": 2.0,
            "rework_rate_percent": 5.0,
            "bottleneck_risk": "low"
        },
        "dependencies": {
            "requires": ["atom-sys-001-soft-credit", "atom-bo-001-assign-lo"],
            "enables": ["atom-sys-002-email-preq"]
        }
    },
    {
        "id": "atom-sys-002-email-preq",
        "name": "Pre-Qualification Letter Email",
        "category": "data_transform",
        "stage": "system",
        "actor": "system",
        "channel": "email",
        "description": "Generate and send pre-qualification letter to borrower via email",
        "estimated_duration_minutes": 1,
        "system_integration": {
            "system_name": "Email Service (SendGrid/AWS SES)",
            "authentication": "api_key",
            "timeout_seconds": 10,
            "retry_policy": "fixed_interval",
            "max_retries": 3
        },
        "dependencies": {
            "requires": ["atom-bo-002-preq-calc"],
            "enables": ["atom-cust-003-preq-letter"]
        }
    },
    {
        "id": "atom-cust-003-preq-letter",
        "name": "Receive Pre-Qualification Letter",
        "category": "communication_receipt",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "email",
        "description": "Borrower receives and reviews pre-qualification letter with estimated loan amount",
        "estimated_duration_minutes": 5,
        "customer_experience": {
            "effort_level": "low",
            "emotional_impact": "positive",
            "nps_impact": 8,
            "pain_points": [],
            "delight_opportunities": ["Clear next steps", "Mobile-friendly format"]
        },
        "dependencies": {
            "requires": ["atom-sys-002-email-preq"],
            "enables": ["atom-cust-004-full-app-start"]
        }
    },

    # === PHASE 2: APPLICATION ===
    {
        "id": "atom-cust-004-full-app-start",
        "name": "Start Full Application (1003)",
        "category": "information_submission",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower begins completing full Uniform Residential Loan Application (Form 1003)",
        "estimated_duration_minutes": 45,
        "customer_experience": {
            "effort_level": "high",
            "emotional_impact": "neutral",
            "nps_impact": -3,
            "pain_points": ["Form length", "Data entry burden", "Technical jargon"],
            "delight_opportunities": ["Save and resume", "Auto-fill from pre-qual", "Tooltips"]
        },
        "regulatory_requirements": [
            {
                "regulation": "HMDA",
                "section": "12 CFR 1003",
                "description": "Collect demographic information (optional for borrower)",
                "deadline_days": 0
            }
        ],
        "dependencies": {
            "requires": ["atom-cust-003-preq-letter"],
            "enables": ["atom-cust-005-app-submit"]
        }
    },
    {
        "id": "atom-cust-005-app-submit",
        "name": "Submit Application",
        "category": "information_submission",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower submits completed 1003 application",
        "estimated_duration_minutes": 10,
        "customer_experience": {
            "effort_level": "medium",
            "emotional_impact": "positive",
            "nps_impact": 5,
            "pain_points": ["Uncertainty about next steps"],
            "delight_opportunities": ["Immediate confirmation", "Clear timeline", "Upload checklist"]
        },
        "regulatory_requirements": [
            {
                "regulation": "TRID",
                "section": "12 CFR 1026.19(e)",
                "description": "Application submission triggers 3-day LE deadline",
                "deadline_days": 3
            },
            {
                "regulation": "ECOA",
                "section": "12 CFR 1002.9",
                "description": "Starts 30-day adverse action timeline",
                "deadline_days": 30
            }
        ],
        "dependencies": {
            "requires": ["atom-cust-004-full-app-start"],
            "enables": ["atom-bo-003-app-review", "atom-sys-003-hard-credit"]
        }
    },
    {
        "id": "atom-sys-003-hard-credit",
        "name": "Hard Credit Pull (Tri-Merge)",
        "category": "api_call",
        "stage": "system",
        "actor": "system",
        "channel": "api",
        "description": "Pull full tri-merge credit report from all three bureaus",
        "estimated_duration_minutes": 3,
        "system_integration": {
            "system_name": "Credit Bureau (Tri-Merge)",
            "authentication": "oauth2",
            "timeout_seconds": 45,
            "retry_policy": "exponential_backoff",
            "max_retries": 2
        },
        "regulatory_requirements": [
            {
                "regulation": "FCRA",
                "section": "15 USC 1681b",
                "description": "Permissible purpose for credit report",
                "deadline_days": 0
            }
        ],
        "dependencies": {
            "requires": ["atom-cust-005-app-submit"],
            "enables": ["atom-bo-003-app-review"]
        }
    },
    {
        "id": "atom-bo-003-app-review",
        "name": "Application Initial Review",
        "category": "document_review",
        "stage": "back_stage",
        "actor": "loan_officer",
        "channel": "web",
        "description": "Loan officer reviews 1003 for completeness and obvious red flags",
        "estimated_duration_minutes": 30,
        "sla_hours": 4,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "semi_automated",
            "error_rate_percent": 5.0,
            "rework_rate_percent": 15.0,
            "bottleneck_risk": "medium"
        },
        "dependencies": {
            "requires": ["atom-cust-005-app-submit", "atom-sys-003-hard-credit"],
            "enables": ["atom-bo-004-doc-request"]
        }
    },
    {
        "id": "atom-bo-004-doc-request",
        "name": "Document Request List Generation",
        "category": "data_validation",
        "stage": "back_stage",
        "actor": "loan_officer",
        "channel": "web",
        "description": "LO generates customized document checklist based on borrower profile",
        "estimated_duration_minutes": 15,
        "sla_hours": 2,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "semi_automated",
            "error_rate_percent": 8.0,
            "rework_rate_percent": 20.0,
            "bottleneck_risk": "low"
        },
        "dependencies": {
            "requires": ["atom-bo-003-app-review"],
            "enables": ["atom-sys-004-email-doc-request"]
        }
    },
    {
        "id": "atom-sys-004-email-doc-request",
        "name": "Email Document Request",
        "category": "data_transform",
        "stage": "system",
        "actor": "system",
        "channel": "email",
        "description": "Send document checklist to borrower with upload portal link",
        "estimated_duration_minutes": 1,
        "system_integration": {
            "system_name": "Email Service",
            "authentication": "api_key",
            "timeout_seconds": 10,
            "retry_policy": "fixed_interval",
            "max_retries": 3
        },
        "dependencies": {
            "requires": ["atom-bo-004-doc-request"],
            "enables": ["atom-cust-006-doc-upload"]
        }
    },
    {
        "id": "atom-cust-006-doc-upload",
        "name": "Upload Documents",
        "category": "information_submission",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower uploads required documents (paystubs, W2s, bank statements, etc.)",
        "estimated_duration_minutes": 30,
        "customer_experience": {
            "effort_level": "high",
            "emotional_impact": "neutral",
            "nps_impact": -5,
            "pain_points": ["Finding documents", "Scanning/photos", "Upload errors"],
            "delight_opportunities": ["Mobile upload", "Progress tracking", "Checklist clarity"]
        },
        "dependencies": {
            "requires": ["atom-sys-004-email-doc-request"],
            "enables": ["atom-bo-005-doc-review"]
        }
    },
    {
        "id": "atom-bo-005-doc-review",
        "name": "Document Review and Classification",
        "category": "document_review",
        "stage": "back_stage",
        "actor": "processor",
        "channel": "web",
        "description": "Processor reviews uploaded docs for legibility, completeness, and classification",
        "estimated_duration_minutes": 45,
        "sla_hours": 24,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "semi_automated",
            "error_rate_percent": 10.0,
            "rework_rate_percent": 25.0,
            "bottleneck_risk": "high"
        },
        "dependencies": {
            "requires": ["atom-cust-006-doc-upload"],
            "enables": ["atom-bo-006-le-preparation"]
        }
    },

    # === PHASE 3: DISCLOSURE ===
    {
        "id": "atom-bo-006-le-preparation",
        "name": "Loan Estimate Preparation",
        "category": "calculation",
        "stage": "back_stage",
        "actor": "loan_officer",
        "channel": "web",
        "description": "Prepare Loan Estimate (LE) with loan terms, estimated costs, and APR",
        "estimated_duration_minutes": 60,
        "sla_hours": 48,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "semi_automated",
            "error_rate_percent": 12.0,
            "rework_rate_percent": 18.0,
            "bottleneck_risk": "high"
        },
        "regulatory_requirements": [
            {
                "regulation": "TRID",
                "section": "12 CFR 1026.19(e)",
                "description": "LE must be delivered within 3 business days of application",
                "deadline_days": 3
            },
            {
                "regulation": "RESPA",
                "section": "12 CFR 1024.7",
                "description": "Good faith estimate of closing costs",
                "deadline_days": 3
            }
        ],
        "dependencies": {
            "requires": ["atom-bo-005-doc-review"],
            "enables": ["atom-sys-005-le-delivery"]
        }
    },
    {
        "id": "atom-sys-005-le-delivery",
        "name": "Loan Estimate Delivery",
        "category": "data_transform",
        "stage": "system",
        "actor": "system",
        "channel": "email",
        "description": "Electronically deliver LE to borrower via email with e-sign capability",
        "estimated_duration_minutes": 2,
        "system_integration": {
            "system_name": "E-signature Platform (DocuSign/Blend)",
            "authentication": "oauth2",
            "timeout_seconds": 15,
            "retry_policy": "exponential_backoff",
            "max_retries": 3
        },
        "regulatory_requirements": [
            {
                "regulation": "TRID",
                "section": "12 CFR 1026.19(e)(1)(iv)",
                "description": "LE delivery triggers 10-business-day intent to proceed waiting period",
                "deadline_days": 10
            }
        ],
        "dependencies": {
            "requires": ["atom-bo-006-le-preparation"],
            "enables": ["atom-cust-007-le-review"]
        }
    },
    {
        "id": "atom-cust-007-le-review",
        "name": "Loan Estimate Review",
        "category": "acknowledgment",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "email",
        "description": "Borrower reviews LE, understands loan terms and estimated costs",
        "estimated_duration_minutes": 20,
        "customer_experience": {
            "effort_level": "medium",
            "emotional_impact": "neutral",
            "nps_impact": 0,
            "pain_points": ["Complex terminology", "Cost surprise"],
            "delight_opportunities": ["Interactive LE", "Video explanation", "LO call"]
        },
        "dependencies": {
            "requires": ["atom-sys-005-le-delivery"],
            "enables": ["atom-cust-008-intent-proceed"]
        }
    },
    {
        "id": "atom-cust-008-intent-proceed",
        "name": "Intent to Proceed",
        "category": "decision_point",
        "stage": "front_stage",
        "actor": "borrower",
        "channel": "web",
        "description": "Borrower indicates intent to proceed with the loan after LE review",
        "estimated_duration_minutes": 5,
        "customer_experience": {
            "effort_level": "low",
            "emotional_impact": "positive",
            "nps_impact": 7,
            "pain_points": [],
            "delight_opportunities": ["Clear next steps", "Processing timeline"]
        },
        "regulatory_requirements": [
            {
                "regulation": "TRID",
                "section": "12 CFR 1026.19(e)(2)(i)(A)",
                "description": "Borrower must indicate intent to proceed before fees collected",
                "deadline_days": 0
            }
        ],
        "dependencies": {
            "requires": ["atom-cust-007-le-review"],
            "enables": ["atom-bo-007-fee-collection", "atom-bo-008-appraisal-order"]
        }
    },
    {
        "id": "atom-bo-007-fee-collection",
        "name": "Collect Application and Credit Fees",
        "category": "data_validation",
        "stage": "back_stage",
        "actor": "loan_officer",
        "channel": "web",
        "description": "Collect application fees and credit report fees (if applicable)",
        "estimated_duration_minutes": 10,
        "sla_hours": 4,
        "sla_unit": "hours",
        "process_metrics": {
            "automation_level": "semi_automated",
            "error_rate_percent": 2.0,
            "rework_rate_percent": 5.0,
            "bottleneck_risk": "low"
        },
        "dependencies": {
            "requires": ["atom-cust-008-intent-proceed"],
            "enables": []
        }
    },

    # Add 40+ more atoms for Processing, Underwriting, CTC, CD, Closing, Funding phases...
    # (Due to length, showing representative sample - the full script would generate all 60+ atoms)
]

def generate_atom_file(atom_def):
    """Generate YAML file for a single atom"""

    # Enrich atom with standard fields
    atom = {
        **atom_def,
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "change_log": [
            {
                "version": "1.0.0",
                "date": datetime.now().isoformat(),
                "author": "System Generator",
                "description": "Initial atom creation",
                "breaking_changes": False
            }
        ],
        "tags": []
    }

    # Determine category subfolder
    if atom["stage"] == "front_stage":
        subfolder = "customer-actions"
    elif atom["stage"] == "back_stage":
        subfolder = "back-office-actions"
    else:
        subfolder = "system-actions"

    # Create directory if not exists
    atom_dir = Path(f"journey-components/atoms/{subfolder}")
    atom_dir.mkdir(parents=True, exist_ok=True)

    # Write YAML file
    filepath = atom_dir / f"{atom['id']}.yaml"
    with open(filepath, 'w') as f:
        yaml.dump(atom, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return str(filepath)

def main():
    """Generate all atoms"""
    print(f"Generating {len(ATOMS)} atoms...")

    generated = []
    for atom_def in ATOMS:
        filepath = generate_atom_file(atom_def)
        generated.append(filepath)
        print(f"✓ Generated: {filepath}")

    print(f"\n✅ Successfully generated {len(generated)} atoms")
    print(f"\nAtoms by stage:")
    front = len([a for a in ATOMS if a["stage"] == "front_stage"])
    back = len([a for a in ATOMS if a["stage"] == "back_stage"])
    system = len([a for a in ATOMS if a["stage"] == "system"])
    print(f"  Front-stage (customer): {front}")
    print(f"  Back-stage (operations): {back}")
    print(f"  System (integration): {system}")

if __name__ == "__main__":
    main()
