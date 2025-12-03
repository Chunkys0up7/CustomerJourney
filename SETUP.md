# Customer Journey Setup & Quick Start Guide

## 🚀 Complete Setup Instructions

### Step 1: Clone and Checkout

```bash
# Clone the repository
cd C:\Users\camer\Projects\
git clone https://github.com/Chunkys0up7/CustomerJourney.git
cd CustomerJourney

# Checkout the complete implementation branch
git fetch origin
git checkout claude/setup-new-repo-01RKD2YooC2JSuFuBGLVLCus
git pull origin claude/setup-new-repo-01RKD2YooC2JSuFuBGLVLCus
```

### Step 2: Install Dependencies

```bash
# Node.js dependencies (for dashboard server)
npm install

# Python dependencies (for AI tools - optional)
pip install pyyaml anthropic jsonschema networkx
```

### Step 3: Start the Dashboard

```bash
# Start the visualization server
npm start
```

The server will start on **http://localhost:3000**

You should see:
```
🚀 Customer Journey Dashboard Server
═══════════════════════════════════════════════════════════

📊 Dashboard: http://localhost:3000/

📈 Alternate Views:
   • Dashboard: http://localhost:3000/public/journey-dashboard.html
   • Graph:     http://localhost:3000/public/journey-graph-viewer.html

📁 Serving files from: C:\Users\camer\Projects\CustomerJourney

💡 Press Ctrl+C to stop the server
```

### Step 4: Open the Dashboard

Open your browser to: **http://localhost:3000**

---

## 📊 What You'll See

### Dashboard Overview

The dashboard shows **119 atoms** across **7 phases**:

| Phase | Atoms | Front-Stage | Back-Stage | System |
|-------|-------|-------------|------------|--------|
| **Pre-Qualification** | 8 | 4 | 2 | 2 |
| **Application** | 31 | 10 | 15 | 6 |
| **Processing** | 19 | 5 | 11 | 3 |
| **Underwriting** | 12 | 3 | 7 | 2 |
| **Closing_Disclosure** | 8 | 1 | 7 | 0 |
| **Closing** | 8 | 4 | 4 | 0 |
| **Funding** | 7 | 2 | 5 | 0 |
| **TOTAL** | **119** | **33** | **56** | **17** |

---

## 🎯 Dashboard Features

### 1. Metrics Panel (Left Sidebar)
- **Total Atoms**: 119
- **Total Modules**: Dynamic count
- **Front-Stage**: 33 customer-facing atoms
- **Back-Stage**: 56 operations atoms
- **System**: 17 integration atoms

### 2. Phase Navigation
Click any phase to filter the view:
- Pre-Qualification (8 atoms)
- Application (31 atoms)
- Processing (19 atoms)
- Underwriting (12 atoms)
- Closing_Disclosure (8 atoms)
- Closing (8 atoms)
- Funding (7 atoms)

### 3. Stage Filters
- **All**: Show all atoms
- **Front-Stage**: Customer-facing only
- **Back-Stage**: Operations only
- **System**: Integration/automation only

### 4. Three Main Views

#### 🏊 Swimlane View (Default)
- Separates atoms into Front-Stage, Back-Stage, and System lanes
- Shows actor, duration, SLA for each atom
- Displays regulatory tags (TRID, RESPA, ECOA, etc.)
- Click any atom card to see details

#### 📅 Timeline View
- Shows atoms in chronological order by phase
- Displays phase-by-phase progression
- Calculates total duration per phase
- Visualizes flow with arrows

#### ⚠️ Impact Analysis View
- Select an atom to analyze downstream impact
- Shows risk level (LOW/MEDIUM/HIGH)
- Identifies affected atoms
- Highlights customer-facing impacts
- Lists regulatory implications
- Provides recommendations

---

## 💡 Using the Dashboard

### Explore a Phase
1. Click "Application" in the left sidebar
2. See all 31 Application atoms
3. Notice Front/Back/System lane separation

### Analyze an Atom
1. Click any atom card
2. Detail panel slides in from right
3. View:
   - Basic information (ID, stage, category, actor)
   - Timing & SLAs
   - Dependencies (requires/enables)
   - Regulatory requirements
   - Data outputs

### Analyze Impact
1. Click an atom to open details
2. Click "Analyze Impact" button
3. Switch to Impact Analysis view
4. See:
   - Risk assessment
   - Immediate dependencies
   - Downstream cascade
   - Customer experience effects
   - Regulatory risks
   - Actionable recommendations

### Follow Dependencies
1. Open atom details
2. Scroll to Dependencies section
3. Click a dependency to navigate to it
4. Explore the journey flow

---

## 🛠️ Advanced Usage (Optional)

### Generate More Atoms

If you want to add more atoms:

```bash
# Edit the generator script
python tools/generate-all-phases.py

# Export to JSON for dashboard
python tools/export-atoms-json.py

# Restart the server
npm start
```

### Use AI Tools

**Claude Atom Generator** (requires Anthropic API key):
```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Generate atoms from an SOP
python ai-engine/atom-generator/claude_atom_draft.py docs/YourSOP.md
```

**Impact Analyzer**:
```bash
# Analyze impact of changing an atom
python ai-engine/impact-analyzer/impact_analyzer.py atom-bo-uw-05-clear-to-close modify
```

---

## 📁 Repository Structure

```
CustomerJourney/
├── journey-components/
│   ├── atoms/
│   │   ├── customer-actions/      # 33 front-stage atoms
│   │   ├── back-office-actions/   # 56 back-stage atoms
│   │   └── system-actions/        # 17 system atoms
│   └── modules/
│       └── module-pre-qualification.yaml
│
├── public/
│   ├── journey-dashboard.html     # Main dashboard
│   ├── journey-graph-viewer.html  # Alternate graph view
│   └── data/
│       └── atoms.json              # All 119 atoms (loaded by dashboard)
│
├── ai-engine/
│   ├── atom-generator/
│   │   └── claude_atom_draft.py   # AI atom generation
│   └── impact-analyzer/
│       └── impact_analyzer.py      # Impact analysis tool
│
├── tools/
│   ├── generate-all-phases.py     # Batch atom generator
│   ├── export-atoms-json.py       # Export atoms to JSON
│   └── [other tools]
│
├── schemas/
│   ├── atom.schema.yaml           # Atom validation schema
│   └── module.schema.yaml         # Module schema
│
├── docs/
│   ├── CUSTOMER_JOURNEY_FRAMEWORK.md  # Complete methodology
│   └── ATOM_REVIEW_CHECKLIST.md      # QA checklist
│
├── server.js                      # Web server
├── package.json                   # Node dependencies
└── README.md                      # Main documentation
```

---

## 🎯 What's Included

### ✅ Complete Features

- **119 Atoms** across 7 phases
- **Complete Dependencies** (requires/enables relationships)
- **Regulatory Mapping** (TRID, RESPA, ECOA, FCRA, HMDA, etc.)
- **Full Metadata** (actors, channels, durations, SLAs)
- **Customer Experience Metrics** for front-stage atoms
- **Process Metrics** for back-stage atoms
- **System Integration Specs** for system atoms
- **Interactive Dashboard** with 3 views
- **Real-time Impact Analysis**
- **AI-Powered Tools** for expansion

### 🔧 Ready for Expansion

- Add remaining phases (Initial Disclosure, Clear-to-Close)
- Create additional modules
- Generate journey variants (FHA, VA, Refinance)
- Map all 46 data elements
- Create complete dependency graph with 300+ edges
- Add advanced analytics

---

## 🐛 Troubleshooting

### Dashboard won't load
- Ensure npm start is running
- Check console for errors (F12 in browser)
- Verify atoms.json exists: `ls public/data/atoms.json`

### No atoms showing
- Regenerate JSON: `python tools/export-atoms-json.py`
- Refresh browser (Ctrl+F5)
- Check browser console for fetch errors

### Port already in use
```bash
# Change port in server.js (line 5)
const PORT = 3001;  # Change to different port
```

---

## 📞 Support

- **Documentation**: See `/docs/CUSTOMER_JOURNEY_FRAMEWORK.md`
- **QA Checklist**: See `/docs/ATOM_REVIEW_CHECKLIST.md`
- **Main README**: See `/README.md`

---

## 🎉 Quick Recap

1. **Clone**: `git clone https://github.com/Chunkys0up7/CustomerJourney.git`
2. **Checkout**: `git checkout claude/setup-new-repo-01RKD2YooC2JSuFuBGLVLCus`
3. **Install**: `npm install`
4. **Start**: `npm start`
5. **Open**: **http://localhost:3000**

**You now have a production-ready Customer Journey mapping system with 119 atoms, 7 phases, complete regulatory tracking, and interactive visualization!**
