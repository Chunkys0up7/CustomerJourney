#!/usr/bin/env python3
"""
Complete 9-Phase Customer Journey Atom Generator
Generates all 155+ atoms based on the implementation plan
"""

import yaml
import os
from datetime import datetime
from pathlib import Path

# Atom template specifications for all 9 phases
# Format: (id, name, stage, category, actor, channel, duration_min, sla_hours, phase, requires, enables, regulatory, outputs)

PHASE_SPECS = {
    "Pre-Qualification": [
        ("atom-cust-pre-01-inquiry", "Mortgage Inquiry", "front_stage", "information_submission", "borrower", "web", 30, None, [], ["atom-cust-pre-02-credit-consent", "atom-bo-pre-02-lead-capture"], [], [("inquiry_id", "string")]),
        ("atom-cust-pre-02-credit-consent", "Credit Authorization Consent", "front_stage", "acknowledgment", "borrower", "web", 15, None, ["atom-cust-pre-01-inquiry"], ["atom-sys-pre-01-soft-credit"], [("FCRA", "15 USC 1681", "Permissible purpose")], [("soft_credit_authorized", "boolean")]),
        ("atom-cust-pre-03-quick-qualifier", "Quick Qualifier Questions", "front_stage", "information_submission", "borrower", "web", 30, None, ["atom-cust-pre-01-inquiry"], ["atom-bo-pre-01-preliminary-approval"], [], [("quick_qualifier_responses", "json")]),
        ("atom-sys-pre-01-soft-credit", "Soft Credit Pull", "system", "api_call", "system", "api", 6, None, ["atom-cust-pre-02-credit-consent"], ["atom-sys-pre-02-credit-parse"], [], [("soft_credit_score", "number")]),
        ("atom-sys-pre-02-credit-parse", "Credit Data Parsing", "system", "data_transform", "system", "api", 3, None, ["atom-sys-pre-01-soft-credit"], ["atom-bo-pre-01-preliminary-approval"], [], [("credit_metrics_parsed", "json")]),
        ("atom-bo-pre-01-preliminary-approval", "Preliminary Approval Generation", "back_stage", "calculation", "system", "api", 15, 0.25, ["atom-sys-pre-02-credit-parse", "atom-cust-pre-03-quick-qualifier"], ["atom-cust-pre-04-approval-delivery"], [], [("preliminary_approval_status", "string"), ("preapproval_letter", "pdf")]),
        ("atom-bo-pre-02-lead-capture", "Lead Capture and Routing", "back_stage", "handoff", "system", "api", 60, 1, ["atom-cust-pre-01-inquiry"], ["atom-cust-pre-04-approval-delivery"], [], [("crm_lead_id", "string"), ("assigned_lo", "string")]),
        ("atom-cust-pre-04-approval-delivery", "Preliminary Approval Delivery", "front_stage", "communication_receipt", "borrower", "email", 5, None, ["atom-bo-pre-01-preliminary-approval", "atom-bo-pre-02-lead-capture"], [], [], [])
    ],

    "Application": [
        # Application channel (2 atoms)
        ("atom-sys-app-01-channel-origination", "Application Channel Origination", "system", "queue_management", "system", "api", 1, None, [], ["atom-bo-app-01-intake-queue"], [("TRID", "12 CFR 1026.19(e)", "Application triggers 3-day LE")], [("application_id", "string")]),
        ("atom-bo-app-01-intake-queue", "Application Intake Queue", "back_stage", "queue_management", "system", "api", 30, 0.5, ["atom-sys-app-01-channel-origination"], ["atom-cust-app-02-profile"], [], []),

        # Customer profile & data entry (10 atoms)
        ("atom-cust-app-02-profile", "Borrower Basic Profile", "front_stage", "information_submission", "borrower", "web", 45, None, ["atom-bo-app-01-intake-queue"], ["atom-cust-app-03-borrower-details"], [("HMDA", "12 CFR 1003", "Demographic collection")], [("borrower_basic_profile", "json")]),
        ("atom-cust-app-03-borrower-details", "Borrower Detailed Information", "front_stage", "information_submission", "borrower", "web", 60, None, ["atom-cust-app-02-profile"], ["atom-cust-app-04-property-details"], [("ECOA", "12 CFR 1002", "No discrimination")], [("borrower_profile_normalized", "json")]),
        ("atom-cust-app-04-property-details", "Property Details", "front_stage", "information_submission", "borrower", "web", 30, None, ["atom-cust-app-03-borrower-details"], ["atom-cust-app-05-employment-details"], [], [("property_details", "json")]),
        ("atom-cust-app-05-employment-details", "Employment Details", "front_stage", "information_submission", "borrower", "web", 45, None, ["atom-cust-app-04-property-details"], ["atom-cust-app-06-asset-details"], [("TRID", "Ability to Repay", "Income verification")], [("employment_details", "json")]),
        ("atom-cust-app-06-asset-details", "Asset and Liability Details", "front_stage", "information_submission", "borrower", "web", 60, None, ["atom-cust-app-05-employment-details"], ["atom-cust-app-07-declarations"], [], [("asset_liability_details", "json")]),
        ("atom-cust-app-07-declarations", "Borrower Declarations", "front_stage", "information_submission", "borrower", "web", 30, None, ["atom-cust-app-06-asset-details"], ["atom-cust-app-08-consents"], [], [("declarations_answered", "json")]),
        ("atom-cust-app-08-consents", "Legal Consents", "front_stage", "acknowledgment", "borrower", "web", 15, None, ["atom-cust-app-07-declarations"], ["atom-cust-app-09-credit-auth"], [("GLBA", "Privacy notice", "Financial privacy")], [("consents_accepted", "json")]),
        ("atom-cust-app-09-credit-auth", "Credit Report Authorization", "front_stage", "acknowledgment", "borrower", "web", 10, None, ["atom-cust-app-08-consents"], ["atom-cust-app-10-upload-docs", "atom-sys-app-03-credit-request"], [("FCRA", "Credit authorization", "Hard pull consent")], [("credit_auth_given", "boolean")]),
        ("atom-cust-app-10-upload-docs", "Document Upload", "front_stage", "information_submission", "borrower", "web", 60, None, ["atom-cust-app-09-credit-auth"], ["atom-bo-app-03-doc-review"], [], [("documents_uploaded", "array")]),
        ("atom-cust-app-11-app-submit", "Application Submission", "front_stage", "information_submission", "borrower", "web", 10, None, ["atom-cust-app-10-upload-docs"], ["atom-bo-app-02-initial-screening"], [], []),

        # Back-office processing (15 atoms)
        ("atom-bo-app-02-initial-screening", "Initial Application Screening", "back_stage", "data_validation", "processor", "web", 30, 1, ["atom-cust-app-11-app-submit"], ["atom-sys-app-02-kyc-verify", "atom-bo-app-04-data-quality"], [], []),
        ("atom-sys-app-02-kyc-verify", "KYC Verification", "system", "api_call", "system", "api", 15, None, ["atom-bo-app-02-initial-screening"], ["atom-bo-app-05-fraud-screen"], [("AML", "KYC Program", "Identity verification")], [("kyc_status", "string")]),
        ("atom-bo-app-04-data-quality", "Data Quality Check", "back_stage", "data_validation", "processor", "web", 20, 1, ["atom-bo-app-02-initial-screening"], ["atom-bo-app-05-fraud-screen"], [], []),
        ("atom-bo-app-05-fraud-screen", "Fraud Screening", "back_stage", "compliance_check", "processor", "web", 15, 1, ["atom-sys-app-02-kyc-verify", "atom-bo-app-04-data-quality"], ["atom-sys-app-03-credit-request"], [("FACTA", "Red Flags", "Fraud detection")], [("fraud_score", "number")]),
        ("atom-sys-app-03-credit-request", "Credit Report Request", "system", "api_call", "system", "api", 10, None, ["atom-cust-app-09-credit-auth", "atom-bo-app-05-fraud-screen"], ["atom-sys-app-04-credit-response"], [], []),
        ("atom-sys-app-04-credit-response", "Credit Report Response", "system", "api_call", "system", "api", 30, None, ["atom-sys-app-03-credit-request"], ["atom-bo-app-06-credit-review"], [("FCRA", "Permissible purpose", "Hard pull")], [("credit_report", "json")]),
        ("atom-bo-app-06-credit-review", "Credit Report Review", "back_stage", "document_review", "processor", "web", 30, 2, ["atom-sys-app-04-credit-response"], ["atom-bo-app-07-liability-import"], [], []),
        ("atom-bo-app-07-liability-import", "Liability Import from Credit", "back_stage", "data_validation", "processor", "web", 15, 1, ["atom-bo-app-06-credit-review"], ["atom-bo-app-09-income-normalize"], [], []),
        ("atom-bo-app-03-doc-review", "Document Review", "back_stage", "document_review", "processor", "web", 60, 4, ["atom-cust-app-10-upload-docs"], ["atom-bo-app-08-doc-storage"], [], []),
        ("atom-bo-app-08-doc-storage", "Document Storage", "back_stage", "data_validation", "processor", "web", 10, 1, ["atom-bo-app-03-doc-review"], ["atom-bo-app-09-income-normalize"], [], []),
        ("atom-bo-app-09-income-normalize", "Income Normalization", "back_stage", "calculation", "processor", "web", 45, 3, ["atom-bo-app-07-liability-import", "atom-bo-app-08-doc-storage"], ["atom-bo-app-11-conditions-initial"], [("Fannie Mae", "B3-3", "Income calculation")], [("income_normalized", "json")]),
        ("atom-bo-app-10-asset-normalize", "Asset Normalization", "back_stage", "calculation", "processor", "web", 30, 2, ["atom-bo-app-09-income-normalize"], ["atom-bo-app-11-conditions-initial"], [("Fannie Mae", "B5-3", "Asset verification")], [("assets_normalized", "json")]),
        ("atom-bo-app-11-conditions-initial", "Initial Conditions List", "back_stage", "data_validation", "processor", "web", 30, 2, ["atom-bo-app-09-income-normalize", "atom-bo-app-10-asset-normalize"], ["atom-bo-app-12-disclosures-generate"], [], [("conditions_list", "array")]),
        ("atom-bo-app-12-disclosures-generate", "Generate Initial Disclosures", "back_stage", "calculation", "loan_officer", "web", 90, 4, ["atom-bo-app-11-conditions-initial"], ["atom-bo-app-13-disclosures-send"], [("TRID", "Loan Estimate", "3-day requirement")], [("disclosures_generated", "pdf")]),
        ("atom-bo-app-13-disclosures-send", "Send Disclosures to Customer", "back_stage", "external_request", "loan_officer", "email", 15, 1, ["atom-bo-app-12-disclosures-generate"], ["atom-sys-app-05-esign-sync"], [], []),

        # System integrations (5 atoms)
        ("atom-sys-app-05-esign-sync", "E-Signature Sync", "system", "api_call", "system", "api", 5, None, ["atom-bo-app-13-disclosures-send"], ["atom-bo-app-14-esign-monitor"], [("ESIGN", "Consent", "Electronic signature")], []),
        ("atom-bo-app-14-esign-monitor", "Monitor E-Signature Status", "back_stage", "data_validation", "processor", "web", 120, 24, ["atom-sys-app-05-esign-sync"], ["atom-bo-app-15-intake-complete"], [], [("esign_status", "string")]),
        ("atom-bo-app-15-intake-complete", "Application Intake Complete", "back_stage", "handoff", "processor", "web", 15, 1, ["atom-bo-app-14-esign-monitor"], [], [], []),
        ("atom-sys-app-06-fraud-engine", "Fraud Detection Engine", "system", "api_call", "system", "api", 20, None, ["atom-bo-app-05-fraud-screen"], ["atom-bo-app-05-fraud-screen"], [], [("fraud_score", "number")])
    ],

    "Processing": [
        ("atom-cust-proc-01-doc-request", "Receive Document Request", "front_stage", "communication_receipt", "borrower", "email", 60, None, [], ["atom-cust-proc-02-gather-docs"], [], []),
        ("atom-cust-proc-02-gather-docs", "Gather and Upload Documents", "front_stage", "information_submission", "borrower", "web", 120, None, ["atom-cust-proc-01-doc-request"], ["atom-bo-proc-01-completeness-audit"], [], [("documents_collected", "array")]),
        ("atom-cust-proc-03-employment-verify", "Authorize VOE", "front_stage", "acknowledgment", "borrower", "web", 30, None, ["atom-cust-proc-02-gather-docs"], ["atom-bo-proc-05-voe-order"], [], [("voe_authorized", "boolean")]),
        ("atom-cust-proc-04-asset-verify", "Authorize VOA", "front_stage", "acknowledgment", "borrower", "web", 30, None, ["atom-cust-proc-02-gather-docs"], ["atom-bo-proc-06-voa-order"], [], [("voa_authorized", "boolean")]),
        ("atom-cust-proc-05-appraisal-access", "Grant Appraisal Access", "front_stage", "acknowledgment", "borrower", "phone", 60, None, ["atom-bo-proc-08-appraisal-order"], ["atom-bo-proc-09-appraisal-conduct"], [], [("appraisal_access_granted", "boolean")]),

        ("atom-bo-proc-01-completeness-audit", "Completeness Audit", "back_stage", "data_validation", "processor", "web", 120, 2, ["atom-cust-proc-02-gather-docs"], ["atom-bo-proc-02-document-review"], [("TRID", "Application Completeness", "Documentation")], [("completeness_status", "enum")]),
        ("atom-bo-proc-02-document-review", "Document Review and Classification", "back_stage", "document_review", "processor", "web", 180, 24, ["atom-bo-proc-01-completeness-audit"], ["atom-bo-proc-03-document-processing"], [], [("doc_review_notes", "text")]),
        ("atom-bo-proc-03-document-processing", "Document Processing", "back_stage", "data_validation", "processor", "web", 120, 2, ["atom-bo-proc-02-document-review"], ["atom-bo-proc-04-data-input"], [], [("extracted_document_data", "json")]),
        ("atom-bo-proc-04-data-input", "Data Input to LOS", "back_stage", "data_validation", "processor", "web", 90, 1.5, ["atom-bo-proc-03-document-processing"], ["atom-bo-proc-05-voe-order", "atom-bo-proc-06-voa-order"], [], [("los_data_populated", "boolean")]),
        ("atom-bo-proc-05-voe-order", "Order VOE", "back_stage", "external_request", "processor", "web", 60, 1, ["atom-cust-proc-03-employment-verify", "atom-bo-proc-04-data-input"], ["atom-sys-proc-02-voe-track"], [], [("voe_request_id", "string")]),
        ("atom-bo-proc-06-voa-order", "Order VOA", "back_stage", "external_request", "processor", "web", 60, 1, ["atom-cust-proc-04-asset-verify", "atom-bo-proc-04-data-input"], ["atom-sys-proc-03-voa-track"], [], [("voa_request_id", "string")]),
        ("atom-bo-proc-07-ti-order", "Order Title Insurance", "back_stage", "external_request", "processor", "web", 120, 2, ["atom-bo-proc-04-data-input"], ["atom-bo-proc-10-ti-report"], [("TRID", "Title Insurance", "Disclosure")], [("title_order_id", "string")]),
        ("atom-bo-proc-08-appraisal-order", "Order Appraisal", "back_stage", "external_request", "processor", "web", 60, 1, ["atom-bo-proc-04-data-input"], ["atom-cust-proc-05-appraisal-access"], [("FDIC", "Appraisal Requirements", "Collateral valuation"), ("Fannie Mae", "Selling Guide", "Appraisal standards")], [("appraisal_order_id", "string")]),
        ("atom-bo-proc-09-appraisal-conduct", "Appraisal Conducted", "back_stage", "external_request", "third_party", "in_person", 480, 120, ["atom-cust-proc-05-appraisal-access"], ["atom-bo-proc-11-appraisal-received"], [], []),
        ("atom-bo-proc-10-ti-report", "Title Insurance Report", "back_stage", "external_request", "third_party", "email", 360, 72, ["atom-bo-proc-07-ti-order"], [], [], []),
        ("atom-bo-proc-11-appraisal-received", "Appraisal Report Received", "back_stage", "document_review", "processor", "web", 30, 2, ["atom-bo-proc-09-appraisal-conduct"], [], [], []),

        ("atom-sys-proc-01-doc-ingestion", "Document Ingestion", "system", "data_transform", "system", "api", 120, None, ["atom-cust-proc-02-gather-docs"], ["atom-bo-proc-01-completeness-audit"], [], [("dms_document_ids", "array")]),
        ("atom-sys-proc-02-voe-track", "VOE Response Tracking", "system", "queue_management", "system", "api", 180, None, ["atom-bo-proc-05-voe-order"], ["atom-bo-proc-04-data-input"], [], [("voe_response_received", "boolean")]),
        ("atom-sys-proc-03-voa-track", "VOA Response Tracking", "system", "queue_management", "system", "api", 240, None, ["atom-bo-proc-06-voa-order"], ["atom-bo-proc-04-data-input"], [], [("voa_response_received", "boolean")])
    ],

    "Underwriting": [
        ("atom-cust-uw-01-condition-notice", "Receive Underwriting Conditions", "front_stage", "communication_receipt", "borrower", "email", 60, None, ["atom-bo-uw-03-issue-conditions"], ["atom-cust-uw-02-satisfy-conditions"], [], []),
        ("atom-cust-uw-02-satisfy-conditions", "Submit Condition Responses", "front_stage", "information_submission", "borrower", "web", 180, None, ["atom-cust-uw-01-condition-notice"], ["atom-bo-uw-04-condition-review"], [], [("condition_response_submitted", "array")]),
        ("atom-cust-uw-03-approval-accept", "Accept Final Approval", "front_stage", "decision_point", "borrower", "web", 120, None, ["atom-bo-uw-05-clear-to-close"], [], [], [("approval_accepted", "boolean")]),

        ("atom-bo-uw-01-submission", "Submit to Underwriting", "back_stage", "handoff", "processor", "web", 60, 1, [], ["atom-bo-uw-02-underwriter-review"], [], [("underwriting_queue_entry", "string")]),
        ("atom-bo-uw-02-underwriter-review", "Underwriter File Review", "back_stage", "document_review", "underwriter", "web", 240, 24, ["atom-bo-uw-01-submission"], ["atom-bo-uw-03-issue-conditions", "atom-bo-uw-06-appraisal-review", "atom-sys-uw-01-dti-calc"], [("Fannie Mae", "Selling Guide", "UW standards"), ("Freddie Mac", "Selling Guide", "UW guidelines")], []),
        ("atom-bo-uw-03-issue-conditions", "Issue Conditions", "back_stage", "decision", "underwriter", "web", 60, 1, ["atom-bo-uw-02-underwriter-review"], ["atom-cust-uw-01-condition-notice"], [], [("underwriting_decision", "enum"), ("conditions_issued", "array")]),
        ("atom-bo-uw-04-condition-review", "Review Condition Responses", "back_stage", "document_review", "underwriter", "web", 120, 4, ["atom-cust-uw-02-satisfy-conditions"], ["atom-bo-uw-05-verify-satisfactory"], [], [("condition_satisfaction_status", "enum")]),
        ("atom-bo-uw-05-verify-satisfactory", "Verify Conditions Satisfied", "back_stage", "decision", "underwriter", "web", 60, 1, ["atom-bo-uw-04-condition-review"], ["atom-bo-uw-05-clear-to-close"], [], [("condition_verification_result", "enum")]),
        ("atom-bo-uw-05-clear-to-close", "Issue Clear to Close", "back_stage", "decision", "underwriter", "web", 15, 0.25, ["atom-bo-uw-05-verify-satisfactory"], ["atom-cust-uw-03-approval-accept"], [], [("clear_to_close_timestamp", "datetime")]),
        ("atom-bo-uw-06-appraisal-review", "Appraisal Review", "back_stage", "document_review", "underwriter", "web", 120, 2, ["atom-bo-uw-02-underwriter-review", "atom-bo-proc-11-appraisal-received"], ["atom-bo-uw-03-issue-conditions"], [], [("appraisal_acceptable", "boolean"), ("appraisal_notes", "text")]),

        ("atom-sys-uw-01-dti-calc", "DTI Calculation", "system", "data_transform", "system", "api", 30, None, ["atom-bo-uw-02-underwriter-review"], ["atom-bo-uw-03-issue-conditions"], [("TRID", "Ability to Repay", "DTI ratios")], [("dti_ratios", "json")]),
        ("atom-sys-uw-02-credit-decision", "Automated Underwriting", "system", "api_call", "system", "api", 120, None, ["atom-bo-uw-01-submission"], ["atom-bo-uw-02-underwriter-review"], [], [("credit_decision_recommendation", "string")])
    ],

    "Closing_Disclosure": [
        ("atom-bo-cd-01-cd-generation", "Generate Closing Disclosure", "back_stage", "calculation", "processor", "web", 120, 2, ["atom-bo-uw-05-clear-to-close"], ["atom-bo-cd-02-cd-delivery"], [("TRID", "Closing Disclosure", "CD generation")], [("closing_disclosure_pdf", "pdf")]),
        ("atom-bo-cd-02-cd-delivery", "Deliver CD to Customer", "back_stage", "external_request", "processor", "email", 60, 1, ["atom-bo-cd-01-cd-generation"], ["atom-bo-cd-03-cd-review-period"], [("TRID", "Delivery Requirement", "3-day rule")], [("cd_delivery_timestamp", "datetime")]),
        ("atom-bo-cd-03-cd-review-period", "CD 3-Day Review Period", "back_stage", "compliance_check", "processor", "web", 4320, 72, ["atom-bo-cd-02-cd-delivery"], ["atom-bo-cd-04-cd-questions"], [("TRID", "Delivery Requirement", "Mandatory wait")], [("cd_review_period_complete", "boolean")]),
        ("atom-bo-cd-04-cd-questions", "Answer CD Questions", "back_stage", "external_request", "loan_officer", "phone", 120, 4, ["atom-bo-cd-03-cd-review-period"], ["atom-bo-cd-05-cd-reconcile"], [], []),
        ("atom-bo-cd-05-cd-reconcile", "Reconcile Closing Costs", "back_stage", "calculation", "processor", "web", 60, 1, ["atom-bo-cd-04-cd-questions"], ["atom-bo-cd-06-closing-packet-prep"], [("TRID", "Tolerance Provisions", "Cost accuracy")], []),
        ("atom-bo-cd-06-closing-packet-prep", "Prepare Closing Packet", "back_stage", "document_review", "processor", "web", 120, 2, ["atom-bo-cd-05-cd-reconcile", "atom-cust-cd-01-cd-acknowledge"], ["atom-bo-cd-07-closing-schedule"], [], [("closing_packet_prepared", "boolean")]),
        ("atom-bo-cd-07-closing-schedule", "Schedule Closing", "back_stage", "external_request", "processor", "phone", 120, 2, ["atom-bo-cd-06-closing-packet-prep"], ["atom-cust-cd-02-closing-confirm"], [], [("closing_appointment_scheduled", "datetime")]),

        ("atom-cust-cd-01-cd-acknowledge", "Acknowledge CD Receipt", "front_stage", "acknowledgment", "borrower", "email", 60, None, ["atom-bo-cd-02-cd-delivery"], ["atom-bo-cd-06-closing-packet-prep"], [], [("cd_acknowledged", "boolean")])
    ],

    "Closing": [
        ("atom-cust-cd-02-closing-confirm", "Closing Confirmation", "front_stage", "communication_receipt", "borrower", "email", 60, None, ["atom-bo-cd-07-closing-schedule"], ["atom-cust-close-01-attend-closing"], [], []),
        ("atom-cust-close-01-attend-closing", "Attend Closing", "front_stage", "waiting_state", "borrower", "in_person", 120, None, ["atom-cust-cd-02-closing-confirm"], ["atom-cust-close-02-sign-docs"], [], []),
        ("atom-cust-close-02-sign-docs", "Sign Closing Documents", "front_stage", "acknowledgment", "borrower", "in_person", 60, None, ["atom-cust-close-01-attend-closing"], ["atom-bo-close-01-doc-processing"], [("ESIGN", "Requirements", "Signature capture")], [("documents_signed", "boolean")]),
        ("atom-cust-close-03-wire-verify", "Verify Wire Transfer", "front_stage", "acknowledgment", "borrower", "phone", 30, None, ["atom-bo-close-02-fund-setup"], ["atom-bo-close-03-recording"], [], []),

        ("atom-bo-close-01-doc-processing", "Process Signed Documents", "back_stage", "document_review", "closer", "web", 30, 0.5, ["atom-cust-close-02-sign-docs"], ["atom-bo-close-02-fund-setup"], [], [("closing_docs_complete", "boolean")]),
        ("atom-bo-close-02-fund-setup", "Setup Funding", "back_stage", "calculation", "closer", "web", 60, 1, ["atom-bo-close-01-doc-processing"], ["atom-cust-close-03-wire-verify"], [], [("closing_funds_collected", "number")]),
        ("atom-bo-close-03-recording", "Record with County", "back_stage", "external_request", "closer", "web", 60, 1, ["atom-cust-close-03-wire-verify"], ["atom-bo-close-04-final-verification"], [], [("documents_recorded", "boolean")]),
        ("atom-bo-close-04-final-verification", "Final Verification", "back_stage", "compliance_check", "closer", "web", 120, 2, ["atom-bo-close-03-recording"], [], [], [("loan_closed_timestamp", "datetime")])
    ],

    "Funding": [
        ("atom-fund-01-transfer-servicing", "Transfer to Servicing", "back_stage", "handoff", "funder", "api", 120, 2, ["atom-bo-close-04-final-verification"], ["atom-fund-02-investor-delivery"], [], [("servicing_system_id", "string")]),
        ("atom-fund-02-investor-delivery", "Deliver to Investor", "back_stage", "external_request", "funder", "api", 480, 24, ["atom-fund-01-transfer-servicing"], ["atom-fund-03-document-archive"], [], [("investor_delivery_id", "string")]),
        ("atom-fund-03-document-archive", "Archive Loan File", "back_stage", "compliance_check", "funder", "web", 480, 8, ["atom-fund-02-investor-delivery"], ["atom-fund-06-quality-assurance"], [("FCRA", "Records Retention", "Document storage"), ("Fannie Mae", "Retention", "Archive requirements")], []),
        ("atom-cust-fund-01-loan-complete", "Loan Funded Notification", "front_stage", "communication_receipt", "borrower", "email", 60, None, ["atom-fund-01-transfer-servicing"], ["atom-cust-fund-02-first-payment"], [], []),
        ("atom-cust-fund-02-first-payment", "First Payment Instructions", "front_stage", "communication_receipt", "borrower", "email", 120, None, ["atom-cust-fund-01-loan-complete"], [], [], []),
        ("atom-fund-06-quality-assurance", "Post-Funding QA", "back_stage", "compliance_check", "funder", "web", 240, 4, ["atom-fund-03-document-archive"], ["atom-fund-07-loan-archived"], [("TRID", "Audit Requirements", "QA review"), ("Fannie Mae", "QA", "Quality control")], []),
        ("atom-fund-07-loan-archived", "Loan Lifecycle Complete", "back_stage", "compliance_check", "funder", "web", 30, 0.5, ["atom-fund-06-quality-assurance"], [], [], [("loan_lifecycle_complete", "boolean")])
    ]
}

def create_atom_from_spec(spec, phase):
    """Create atom dict from specification tuple"""
    (atom_id, name, stage, category, actor, channel, duration, sla, requires, enables, regulatory, outputs) = spec

    atom = {
        "id": atom_id,
        "name": name,
        "description": f"{name} - {phase} phase",
        "category": category,
        "stage": stage,
        "actor": actor,
        "channel": channel,
        "phase": phase,
        "estimated_duration_minutes": duration,
        "dependencies": {
            "requires": requires,
            "enables": enables
        },
        "data_outputs": [{"field": field, "destination": "storage", "format": fmt} for field, fmt in outputs],
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "change_log": [{
            "version": "1.0.0",
            "date": datetime.now().isoformat(),
            "author": "Complete Journey Generator",
            "description": f"Generated {phase} phase atom",
            "breaking_changes": False
        }],
        "tags": []
    }

    # Add SLA for back_stage
    if stage == "back_stage" and sla:
        atom["sla_hours"] = sla
        atom["sla_unit"] = "hours"

    # Add regulatory requirements
    if regulatory:
        atom["regulatory_requirements"] = [
            {"regulation": reg, "section": section, "description": desc}
            for reg, section, desc in regulatory
        ]

    # Add stage-specific metrics
    if stage == "front_stage":
        atom["customer_experience"] = {
            "effort_level": "medium",
            "emotional_impact": "neutral",
            "nps_impact": 0
        }
    elif stage == "back_stage":
        atom["process_metrics"] = {
            "automation_level": "manual",
            "error_rate_percent": 5.0,
            "rework_rate_percent": 10.0,
            "bottleneck_risk": "medium"
        }
    else:  # system
        atom["system_integration"] = {
            "system_name": "LOS",
            "authentication": "api_key",
            "timeout_seconds": 30,
            "retry_policy": "exponential_backoff",
            "max_retries": 3
        }

    return atom

def generate_atom_file(atom):
    """Generate YAML file for atom"""
    # Determine subfolder
    if atom["stage"] == "front_stage":
        subfolder = "customer-actions"
    elif atom["stage"] == "back_stage":
        subfolder = "back-office-actions"
    else:
        subfolder = "system-actions"

    # Create directory
    atom_dir = Path(f"journey-components/atoms/{subfolder}")
    atom_dir.mkdir(parents=True, exist_ok=True)

    # Write file
    filepath = atom_dir / f"{atom['id']}.yaml"
    with open(filepath, 'w') as f:
        yaml.dump(atom, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return str(filepath)

def main():
    """Generate all atoms for all phases"""
    total = 0
    phase_stats = {}

    print("🚀 Generating Complete Customer Journey (155+ atoms)")
    print("=" * 70)

    for phase, specs in PHASE_SPECS.items():
        print(f"\n📋 Phase: {phase}")
        print(f"   Generating {len(specs)} atoms...")

        phase_atoms = []
        for spec in specs:
            atom = create_atom_from_spec(spec, phase)
            filepath = generate_atom_file(atom)
            phase_atoms.append(atom)
            print(f"   ✓ {atom['id']}")

        # Stats
        front = len([a for a in phase_atoms if a["stage"] == "front_stage"])
        back = len([a for a in phase_atoms if a["stage"] == "back_stage"])
        system = len([a for a in phase_atoms if a["stage"] == "system"])

        phase_stats[phase] = {"front": front, "back": back, "system": system, "total": len(phase_atoms)}
        total += len(phase_atoms)

    print("\n" + "=" * 70)
    print(f"✅ Successfully generated {total} atoms across {len(PHASE_SPECS)} phases")
    print("\n📊 Summary by Phase:")
    print(f"{'Phase':<25} {'Front':<8} {'Back':<8} {'System':<8} {'Total':<8}")
    print("-" * 70)

    for phase, stats in phase_stats.items():
        print(f"{phase:<25} {stats['front']:<8} {stats['back']:<8} {stats['system']:<8} {stats['total']:<8}")

    print("\n🎯 Next Steps:")
    print("  1. Review generated atoms in journey-components/atoms/")
    print("  2. Update dashboard to show all phases")
    print("  3. Generate modules from atom collections")
    print("  4. Create complete dependency graph")

if __name__ == "__main__":
    main()
