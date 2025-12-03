# Atom Review Checklist

Use this checklist when reviewing AI-generated or manually-created atoms before adding them to the journey graph.

---

## ✅ Identity & Classification

- [ ] **ID Format**: Follows `atom-{type}-{seq}-{short-name}` pattern
  - `atom-cust-001-inquiry` ✓
  - `atom-bo-005-income-validation` ✓
  - `atom-sys-003-hard-credit` ✓

- [ ] **Name**: Clear, human-readable (5-100 characters)

- [ ] **Description**: Detailed (20-500 characters), explains what happens

- [ ] **Category**: Matches taxonomy
  - Front-stage: `information_submission`, `decision_point`, `acknowledgment`, `communication_receipt`, `waiting_state`
  - Back-stage: `data_validation`, `document_review`, `calculation`, `decision`, `external_request`, `compliance_check`, `handoff`
  - System: `api_call`, `data_transform`, `queue_management`, `timer_event`

- [ ] **Stage**: Correct classification
  - `front_stage` - Customer directly interacts
  - `back_stage` - Internal operation, invisible to customer
  - `system` - Automated process

---

## ✅ Actor & Channel

- [ ] **Actor**: Appropriate for stage
  - Front: `borrower`, `co_borrower`
  - Back: `loan_officer`, `processor`, `underwriter`, `closer`
  - System: `system`, `third_party`

- [ ] **Channel**: Realistic
  - `web`, `mobile`, `email`, `phone`, `in_person`, `api`, `batch`

---

## ✅ Timing & SLAs

- [ ] **Estimated Duration**: Realistic (in minutes)
  - Consider: Industry standards, automation level, complexity

- [ ] **SLA Hours** (back-stage only): Reasonable business hours

- [ ] **SLA Unit**: Appropriate (`business_days`, `calendar_days`, `hours`)

---

## ✅ Dependencies

- [ ] **Requires**: Lists atoms that MUST complete first
  - Check: Do these atoms actually exist?
  - Check: Are they logically prerequisite?

- [ ] **Enables**: Lists atoms that this unlocks
  - Check: Bidirectional consistency (if A enables B, B should require A)

- [ ] **Parallel With**: Lists atoms that can run concurrently
  - Check: No circular dependencies
  - Check: No conflicting data requirements

- [ ] **No Orphans**: Atom connects to at least one other atom (unless it's a start/end node)

---

## ✅ Data Flow

- [ ] **Data Inputs**: All required inputs identified
  - Field name is clear
  - Source is valid (atom ID or "external")
  - Required flag is accurate

- [ ] **Data Outputs**: Outputs are consumed by downstream atoms
  - Check: Destination atoms actually use this data

- [ ] **Data Formats**: Specified and consistent
  - `string`, `number`, `date`, `boolean`, `object`, `array`

---

## ✅ Regulatory Compliance

- [ ] **Regulations Identified**: All applicable regulations listed
  - TRID, RESPA, ECOA, FCRA, HMDA, FHA, VA, USDA, Fannie Mae, Freddie Mac

- [ ] **Sections Cited**: Specific regulation sections referenced

- [ ] **Deadlines Accurate**: Deadline days match actual regulations
  - Example: TRID LE = 3 business days
  - Example: TRID CD = 7 business days before closing

- [ ] **Compliance Description**: Clear explanation of what's required

---

## ✅ Customer Experience (front-stage only)

- [ ] **Effort Level**: Realistic assessment
  - `low`: < 10 minutes, simple action
  - `medium`: 10-30 minutes, moderate complexity
  - `high`: > 30 minutes, significant burden

- [ ] **Emotional Impact**: Honest assessment
  - `negative`: Frustration, anxiety, confusion
  - `neutral`: Neither positive nor negative
  - `positive`: Delight, confidence, satisfaction

- [ ] **NPS Impact**: Justified (-10 to +10)
  - Negative: Delays, errors, poor communication
  - Positive: Speed, clarity, personalization

- [ ] **Pain Points**: Specific and actionable

- [ ] **Delight Opportunities**: Realistic and valuable

---

## ✅ Process Metrics (back-stage only)

- [ ] **Automation Level**: Accurate
  - `manual`: Human performs all steps
  - `semi_automated`: Mix of human and system
  - `automated`: Fully automated

- [ ] **Error Rate**: Based on data or industry benchmarks

- [ ] **Rework Rate**: Realistic percentage

- [ ] **Bottleneck Risk**: Justified
  - `high`: Frequently causes delays
  - `medium`: Occasionally problematic
  - `low`: Rarely a bottleneck

---

## ✅ System Integration (system stage only)

- [ ] **System Name**: Clearly identified

- [ ] **API Endpoint**: Valid (if applicable)

- [ ] **Authentication**: Appropriate method
  - `oauth2`, `api_key`, `basic_auth`, `certificate`

- [ ] **Timeout**: Reasonable (1-300 seconds)

- [ ] **Retry Policy**: Appropriate for system
  - `none`: Single attempt only
  - `exponential_backoff`: For transient failures
  - `fixed_interval`: For predictable delays

- [ ] **Max Retries**: Reasonable (0-10)

---

## ✅ SOP Links

- [ ] **SOP IDs**: Valid references to existing SOPs

- [ ] **Relevance**: Accurate classification
  - `primary`: This SOP defines this atom
  - `supporting`: Provides context or detail
  - `reference`: Related information

- [ ] **Sections Cited**: Specific SOP sections referenced

---

## ✅ Versioning

- [ ] **Version**: Follows semver (`major.minor.patch`)

- [ ] **Last Updated**: ISO 8601 timestamp

- [ ] **Change Log**: Complete and descriptive
  - Version number
  - Date
  - Author
  - Description
  - Breaking changes flag

---

## ✅ Quality Checks

- [ ] **No Typos**: Grammar and spelling checked

- [ ] **Consistent Terminology**: Uses standard mortgage terms

- [ ] **Realistic**: Reflects actual industry practices

- [ ] **Complete**: All required fields present

- [ ] **Validated**: Passes schema validation
  ```bash
  python tools/validate.py journey-components/atoms/
  ```

---

## ✅ Impact Analysis

Before finalizing the atom:

- [ ] **Impact Analyzed**: Run impact analysis
  ```bash
  python ai-engine/impact-analyzer/impact_analyzer.py {atom-id} add
  ```

- [ ] **Dependencies Reviewed**: Check all affected atoms

- [ ] **Customer Experience Assessed**: Review CX impact

- [ ] **Regulatory Implications**: Confirm compliance

---

## ✅ Final Approval

- [ ] **Reviewed By**: Process owner (LO, Processor, UW, etc.)

- [ ] **Approved By**: Operations manager or compliance officer

- [ ] **Integrated**: Added to journey graph

- [ ] **Visualized**: Appears correctly in graph viewer

---

## Common Issues & Solutions

### Issue: Circular Dependencies
**Problem**: Atom A requires B, B requires C, C requires A

**Solution**: Redesign atoms to break the cycle. Often one step should actually be parallel or conditional.

---

### Issue: Overly Broad Atoms
**Problem**: Atom tries to do too much (e.g., "Complete Underwriting")

**Solution**: Break into smaller, indivisible atoms following NASA atomic principles.

---

### Issue: Missing Regulatory Requirements
**Problem**: Atom involves regulated activity but has no compliance references

**Solution**: Review TRID, RESPA, ECOA, FCRA requirements for this step. Consult compliance officer.

---

### Issue: Unrealistic SLAs
**Problem**: SLA doesn't match actual performance

**Solution**: Use historical data. Underpromise and overdeliver.

---

### Issue: Inconsistent Dependencies
**Problem**: Atom A enables B, but B doesn't require A

**Solution**: Dependencies must be bidirectional. Fix both atoms.

---

## Reviewer Sign-Off

**Atom ID:** ______________________________

**Reviewer Name:** ______________________________

**Review Date:** ______________________________

**Approved:** ☐ Yes  ☐ No (see comments)

**Comments:**

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________
