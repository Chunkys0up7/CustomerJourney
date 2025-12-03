# Customer Journey as Code

> Applying NASA-STD-2100-91 atomic/modular documentation principles to mortgage origination customer journeys

## 🎯 Overview

This project transforms customer journey mapping from static documentation into living, executable code. By applying NASA's atomic documentation principles (NASA-STD-2100-91) to mortgage origination, we create:

- **Atomic Touchpoints**: Smallest indivisible customer interactions
- **Modular Workflows**: Composable sets of related touchpoints
- **Phased Journeys**: Major stages in the customer experience
- **Graph-Based Architecture**: Dependency tracking and impact analysis

## 🌟 Key Features

### 1. **Atomic Decomposition**
Every customer touchpoint is an "atom" - a self-contained, reusable unit with:
- Actor identification (customer, processor, underwriter, system)
- Front-stage vs back-stage distinction
- SLA tracking
- Regulatory compliance mapping
- Customer sentiment analysis

### 2. **Impact Analysis** 🔥
The killer feature: Analyze downstream effects of any change
```bash
npm run impact atom-cust-income-w2-upload modify
```
Shows:
- Affected customer touchpoints
- Regulatory implications
- SLA impacts
- Risk scoring
- Recommended actions

### 3. **Graph Validation**
Comprehensive validation ensures graph integrity:
```bash
npm run validate
```
Checks:
- Schema compliance
- Broken references
- Orphaned nodes
- Circular dependencies
- SLA consistency

### 4. **Comprehensive Dashboard** 🎨
Multi-view dashboard with:
- **Swimlane View**: Front-stage/Back-stage/System separation
- **Timeline View**: Phase-by-phase progression with atom flow
- **Impact Analysis**: Real-time dependency analysis with risk scoring
- **Overview Panel**: Journey metrics, phase navigation, filters
- **Detail Panel**: Slide-in atom details with dependencies and regulatory info
- **Interactive**: Click atoms for details, analyze impact, view in context

### 5. **AI-Powered Atom Generator**
Rapidly create new touchpoints:
```bash
npm run generate "Customer uploads bank statements"
```
Auto-detects:
- Actor type
- Customer visibility
- Appropriate SLA
- Output directory

## 📁 Project Structure

```
customer-journey/
├── journey-components/
│   ├── atoms/
│   │   ├── customer-actions/      # Customer-facing touchpoints (front-stage)
│   │   ├── back-office-actions/   # Internal operations (back-stage)
│   │   └── system-actions/        # Automated processes (system)
│   ├── modules/                   # Workflow compositions (DIDs)
│   ├── phases/                    # Journey stages
│   └── journeys/                  # Complete end-to-end journeys
├── ai-engine/
│   ├── atom-generator/
│   │   └── claude_atom_draft.py   # AI-powered atom generation with Claude API
│   └── impact-analyzer/
│       └── impact_analyzer.py     # Comprehensive impact analysis tool
├── schemas/
│   ├── atom.schema.yaml           # Complete atom schema definition
│   └── module.schema.yaml         # Module schema definition
├── graph/
│   └── customer-journey-graph.json  # Master graph database
├── tools/
│   ├── build-journey.js           # Build complete journey docs
│   ├── impact-analysis.js         # Analyze change impacts
│   ├── validate-graph.js          # Validate graph integrity
│   ├── generate-atom.js           # Generate new atoms
│   └── generate-atoms-batch.py    # Batch atom generation
├── public/
│   └── journey-graph-viewer.html  # Interactive visualization
├── dist/
│   └── journeys/                  # Generated documentation
├── docs/
│   ├── CUSTOMER_JOURNEY_FRAMEWORK.md  # Complete methodology & framework
│   ├── ATOM_REVIEW_CHECKLIST.md      # QA checklist for atoms
│   └── IMPLEMENTATION_GUIDE.md       # Implementation guide
└── server.js                       # Visualization web server

```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
cd customer-journey
npm install

# Validate the graph
npm run validate

# Build journey documentation
npm run build

# Analyze impact of a change
npm run impact atom-cust-income-w2-upload

# Generate a new atom
npm run generate "Processor reviews credit report"

# Start visualization server
npm start
# Then open http://localhost:3000
```

**The comprehensive dashboard provides:**
- **📊 Overview Dashboard** - Real-time metrics, phase navigation, and filters
- **🏊 Swimlane View** - Front-stage/Back-stage/System lane separation
- **📅 Timeline View** - Phase-by-phase journey progression with flow
- **⚠️ Impact Analysis** - Interactive dependency analysis with risk scoring
- **🔍 Atom Details** - Slide-in panel with complete atom information and quick actions

---

## 🤖 AI-Powered Tools

### Claude Atom Generator

Automatically generate atoms from SOP documentation using Claude AI:

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Generate atoms from an SOP
python ai-engine/atom-generator/claude_atom_draft.py docs/SOP-Income-Verification.md

# The tool will:
# 1. Read the SOP
# 2. Use Claude to identify atomic steps
# 3. Classify each as front-stage/back-stage/system
# 4. Map to taxonomy categories
# 5. Extract regulatory requirements
# 6. Estimate timing and SLAs
# 7. Generate complete YAML files
```

**Features:**
- Analyzes SOP/process documentation
- Identifies indivisible atoms
- Classifies stage (front/back/system) and category
- Maps to regulatory requirements (TRID, RESPA, ECOA, etc.)
- Extracts dependencies
- Provides realistic timing estimates
- Generates schema-compliant YAML

### Python Impact Analyzer

Comprehensive impact analysis for atom changes:

```bash
# Analyze impact of modifying an atom
python ai-engine/impact-analyzer/impact_analyzer.py atom-bo-005-income-validation modify

# Generate JSON report
python ai-engine/impact-analyzer/impact_analyzer.py atom-bo-005-income-validation modify --report-format=json
```

**Analysis includes:**
- Immediate dependencies (direct impact)
- Downstream dependencies (cascading impact)
- Customer-facing impacts (CX assessment)
- Regulatory impacts (compliance risk)
- SLA cascade (timing implications)
- Risk scoring (LOW/MEDIUM/HIGH)
- Actionable recommendations

**Change types:**
- `modify` - Changing timing, requirements, or outputs
- `remove` - Removing an atom entirely
- `add` - Adding a new atom

---

## 📊 Sample Journey: Conventional Purchase

The included sample demonstrates a simplified mortgage origination journey:

### Phase: Processing
**Module: Income Verification** (86.1h SLA)

1. **Customer Submits Application** (0.5h)
   - Front-stage, customer action
   - Entry point for journey
   - TRID compliance trigger

2. **Customer Uploads W-2 Forms** (24h)
   - Front-stage, customer action
   - Document portal interaction
   - OCR validation

3. **Processor Reviews Income Documents** (8h)
   - Back-stage, processor action
   - Quality control checkpoint
   - Compliance verification

4. **Calculate Qualifying Income** (4h)
   - Back-stage, processor action
   - ATR/QM compliance critical
   - Fannie Mae/Freddie Mac formulas

5. **Submit to Automated Underwriting** (0.25h)
   - Back-stage, system action
   - AUS integration (DU/LPA)
   - Instant risk assessment

6. **Underwriter Issues Decision** (48h)
   - Front-stage, underwriter action
   - Customer-visible milestone
   - Multiple regulatory requirements

**Total Module SLA**: 86.1 hours (3.6 days)

## 🔍 Impact Analysis Example

Analyzing changes to "Customer Uploads W-2 Forms":

```
📋 IMPACT ANALYSIS REPORT
═══════════════════════════════════════════════════════════════════

🎯 Atom: Customer Uploads W-2 Forms
   Change Type: MODIFY
   Risk Level: 🔴 CRITICAL

📈 Downstream Impact:
   Total touchpoints affected: 5
   Customer-facing impacts: 1
   Back-office impacts: 3
   System integrations: 1
   Regulatory touchpoints: 4

⏱️ Timeline Impact:
   Total downstream SLA: 86.1 hours (3.6 days)

💡 Recommendations:
   🔴 Compliance [CRITICAL]: Legal/Compliance review required
   🟠 Customer Experience [HIGH]: Test customer-facing touchpoints
   🟠 Timeline [HIGH]: Review SLA commitments
   🟡 Technology [MEDIUM]: IT system testing required
```

## 🏗️ Architecture Principles

### NASA-STD-2100-91 Adaptation

1. **Atomicity**: Each touchpoint is self-contained
2. **Modularity**: Atoms compose into workflows
3. **Hierarchy**: Modules → Phases → Journeys
4. **Reusability**: Atoms used across multiple journeys
5. **Version Control**: All components in Git
6. **Documentation as Code**: YAML + JSON + Markdown

### Front-Stage vs Back-Stage

Inspired by service design blueprinting:

- **Front-Stage**: Customer-visible interactions (waiting, uploading docs, receiving decisions)
- **Back-Stage**: Internal operations (underwriting, processing, system integrations)

This distinction enables:
- Customer experience optimization
- Operational efficiency analysis
- Technology investment prioritization

## 📏 Metrics & KPIs

### Journey-Level Metrics
- Application completion rate
- Time to decision
- Customer satisfaction (CSAT)
- Net Promoter Score (NPS)
- Pull-through rate
- Closing rate

### Atom-Level Metrics
- Touchpoint completion rate
- Average time per touchpoint
- Error/re-work rate
- Customer effort score
- Compliance audit success rate

## 🔐 Regulatory Compliance

Built-in compliance tracking for:
- **TRID** (TILA-RESPA Integrated Disclosure)
- **ECOA** (Equal Credit Opportunity Act)
- **ATR/QM** (Ability to Repay / Qualified Mortgage)
- **FCRA** (Fair Credit Reporting Act)
- **Fannie Mae Selling Guide**
- **Freddie Mac Selling Guide**

Each atom includes `regulatory_refs` field linking touchpoints to requirements.

## 🎨 Visualization

The interactive graph viewer provides:

### Color Coding (by Actor)
- 🟢 **Green**: Customer actions
- 🔵 **Blue**: Processor actions
- 🟣 **Purple**: Underwriter actions
- 🟠 **Orange**: System actions
- 🔷 **Cyan**: Loan Officer actions
- 🔴 **Red**: Closer actions

### Node Sizes
- **Large (30px)**: Complete journeys
- **Medium (25px)**: Phases
- **Medium-Small (20px)**: Modules
- **Small (15px)**: Atoms

### Edge Types
- **Solid**: Sequential, enables, triggers
- **Dashed**: Contains (hierarchical)

## 🛠️ Advanced Usage

### Creating a New Journey

1. **Define Atoms** (touchpoints):
```bash
npm run generate "Customer reviews initial disclosures"
npm run generate "Processor orders appraisal"
npm run generate "Appraiser inspects property"
```

2. **Update Graph** (`graph/customer-journey-graph.json`):
   - Add atom nodes
   - Create module to group related atoms
   - Add phase containing modules
   - Add journey containing phases
   - Define edges (dependencies)

3. **Validate**:
```bash
npm run validate
```

4. **Build Documentation**:
```bash
npm run build
```

5. **Analyze Impact**:
```bash
npm run impact atom-processor-orders-appraisal
```

### Extending the Framework

See `docs/IMPLEMENTATION_GUIDE.md` for:
- Adding new atom types
- Custom validation rules
- Integration with external systems
- Scaling to 100+ atoms

## 📈 Roadmap

### Phase 1: Foundation (Current)
- ✅ Atomic decomposition framework
- ✅ Graph-based architecture
- ✅ Impact analysis tool
- ✅ Interactive visualization

### Phase 2: Enhanced Analytics
- [ ] Timeline simulation
- [ ] Bottleneck identification
- [ ] Customer sentiment tracking
- [ ] Conversion funnel analysis

### Phase 3: AI Integration
- [ ] Automated atom generation from documents
- [ ] Predictive SLA forecasting
- [ ] Intelligent workflow optimization
- [ ] Compliance risk scoring

### Phase 4: Enterprise Features
- [ ] Multi-journey comparison
- [ ] A/B testing framework
- [ ] Real-time metrics dashboard
- [ ] API for external integrations

## 🤝 Contributing

This is a demonstration framework. To adapt for your organization:

1. Clone the repository
2. Modify `graph/customer-journey-graph.json` with your journeys
3. Create atom YAML files for your touchpoints
4. Customize validation rules in `tools/validate-graph.js`
5. Adjust actor colors in `public/journey-graph-viewer.html`

## 📚 Additional Resources

- [NASA-STD-2100-91 Standard](https://standards.nasa.gov/)
- [Service Design Blueprinting](https://www.nngroup.com/articles/service-blueprints-definition/)
- [TRID Compliance Guide](https://www.consumerfinance.gov/compliance/compliance-resources/mortgage-resources/tila-respa-integrated-disclosures/)
- [Fannie Mae Selling Guide](https://singlefamily.fanniemae.com/selling-guide)

## 📄 License

MIT License - Feel free to adapt for your organization

## 🙏 Acknowledgments

- **NASA-STD-2100-91**: Atomic/modular documentation principles
- **Service Design**: Front-stage/back-stage concepts
- **D3.js**: Interactive visualization library
- **Mortgage Industry**: Domain expertise and compliance requirements

---

**Built with ❤️ using Customer Journey as Code**

*Transforming static journey maps into living, executable documentation*
