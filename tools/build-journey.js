#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class CustomerJourneyBuilder {
  constructor() {
    this.graphPath = path.join(__dirname, '..', 'graph', 'customer-journey-graph.json');
    this.componentsDir = path.join(__dirname, '..', 'journey-components');
    this.outputDir = path.join(__dirname, '..', 'dist', 'journeys');
    this.graph = null;
    this.components = new Map();
  }

  async build() {
    console.log('🚀 Customer Journey Builder starting...\n');

    try {
      // Load graph
      console.log('📊 Loading journey graph...');
      this.loadGraph();

      // Load all YAML components
      console.log('📄 Loading journey components...');
      await this.loadComponents();

      // Ensure output directory exists
      if (!fs.existsSync(this.outputDir)) {
        fs.mkdirSync(this.outputDir, { recursive: true });
      }

      // Build all journeys
      console.log('🔨 Building journeys...\n');
      const journeys = this.findJourneyNodes();

      for (const journeyId of journeys) {
        await this.buildJourney(journeyId);
      }

      console.log('\n✅ Build complete!');
      console.log(`📁 Output directory: ${this.outputDir}`);

    } catch (error) {
      console.error('❌ Build failed:', error.message);
      process.exit(1);
    }
  }

  loadGraph() {
    try {
      const graphData = fs.readFileSync(this.graphPath, 'utf8');
      this.graph = JSON.parse(graphData);
      console.log(`   ✓ Loaded graph with ${this.graph.metadata.stats.atomCount} atoms\n`);
    } catch (error) {
      throw new Error(`Failed to load graph: ${error.message}`);
    }
  }

  async loadComponents() {
    const atomTypes = ['customer-actions', 'back-office-actions', 'system-actions'];

    for (const atomType of atomTypes) {
      const atomDir = path.join(this.componentsDir, 'atoms', atomType);

      if (!fs.existsSync(atomDir)) continue;

      const files = fs.readdirSync(atomDir).filter(f => f.endsWith('.yaml'));

      for (const file of files) {
        const filePath = path.join(atomDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const component = yaml.load(content);
        this.components.set(component.id, component);
      }
    }

    console.log(`   ✓ Loaded ${this.components.size} components\n`);
  }

  findJourneyNodes() {
    return Object.keys(this.graph.nodes).filter(
      id => this.graph.nodes[id].type === 'journey'
    );
  }

  async buildJourney(journeyId) {
    const journeyNode = this.graph.nodes[journeyId];
    console.log(`📝 Building: ${journeyNode.title}`);

    let markdown = this.buildJourneyHeader(journeyNode);
    markdown += this.buildJourneyOverview(journeyNode);
    markdown += await this.buildPhases(journeyNode);
    markdown += this.buildTimeline(journeyNode);
    markdown += this.buildMetrics(journeyNode);

    // Write to file
    const filename = `${journeyId}.md`;
    const outputPath = path.join(this.outputDir, filename);
    fs.writeFileSync(outputPath, markdown, 'utf8');

    console.log(`   ✓ Generated: ${filename}`);
  }

  buildJourneyHeader(journeyNode) {
    return `# ${journeyNode.title}

> **Journey ID:** \`${journeyNode.id}\`
> **Type:** ${journeyNode.loan_type} | ${journeyNode.transaction_type}
> **Target SLA:** ${journeyNode.sla_days} days

---

`;
  }

  buildJourneyOverview(journeyNode) {
    return `## Overview

${journeyNode.description}

**Key Characteristics:**
- **Loan Type:** ${journeyNode.loan_type}
- **Transaction Type:** ${journeyNode.transaction_type}
- **Expected Timeline:** ${journeyNode.sla_days} days from application to closing

---

`;
  }

  async buildPhases(journeyNode) {
    let markdown = `## Journey Phases\n\n`;

    for (const phaseId of journeyNode.phases) {
      const phaseNode = this.graph.nodes[phaseId];

      markdown += `### ${phaseNode.title}\n\n`;
      markdown += `${phaseNode.description}\n\n`;
      markdown += `**SLA:** ${phaseNode.sla_hours} hours (${(phaseNode.sla_hours / 24).toFixed(1)} days)\n\n`;

      // Build modules within phase
      if (phaseNode.modules && phaseNode.modules.length > 0) {
        markdown += await this.buildModules(phaseNode);
      }
    }

    markdown += `---\n\n`;
    return markdown;
  }

  async buildModules(phaseNode) {
    let markdown = '';

    for (const moduleId of phaseNode.modules) {
      const moduleNode = this.graph.nodes[moduleId];

      markdown += `#### ${moduleNode.title}\n\n`;
      markdown += `${moduleNode.description}\n\n`;
      markdown += `**Module SLA:** ${moduleNode.sla_hours} hours\n\n`;

      // Build atoms within module
      if (moduleNode.atoms && moduleNode.atoms.length > 0) {
        markdown += await this.buildAtoms(moduleNode);
      }
    }

    return markdown;
  }

  async buildAtoms(moduleNode) {
    let markdown = `**Touchpoints:**\n\n`;

    for (const atomId of moduleNode.atoms) {
      const atomNode = this.graph.nodes[atomId];
      const atomComponent = this.components.get(atomId);

      markdown += `##### ${atomNode.title}\n\n`;
      markdown += `| Property | Value |\n`;
      markdown += `|----------|-------|\n`;
      markdown += `| **Atom ID** | \`${atomId}\` |\n`;
      markdown += `| **Actor** | ${atomNode.actor} |\n`;
      markdown += `| **Type** | ${atomNode.atom_type} |\n`;
      markdown += `| **Customer Visible** | ${atomNode.customer_visible ? '✓ Yes' : '✗ No'} |\n`;
      markdown += `| **Front Stage** | ${atomNode.front_stage ? '✓ Yes' : '✗ No'} |\n`;
      markdown += `| **SLA** | ${atomNode.sla_hours} hours |\n`;

      if (atomNode.regulatory_refs && atomNode.regulatory_refs.length > 0) {
        markdown += `| **Regulatory** | ${atomNode.regulatory_refs.join(', ')} |\n`;
      }

      markdown += `\n`;

      // Add description from component if available
      if (atomComponent && atomComponent.description) {
        markdown += `${atomComponent.description}\n\n`;
      }

      // Add steps if available
      if (atomComponent && atomComponent.steps && atomComponent.steps.length > 0) {
        markdown += `**Steps:**\n\n`;
        for (const step of atomComponent.steps) {
          markdown += `${step.step}. ${step.action}\n`;
          if (step.details) markdown += `   - ${step.details}\n`;
          if (step.regulatory) markdown += `   - 📋 ${step.regulatory}\n`;
          if (step.trigger) markdown += `   - 🔔 ${step.trigger}\n`;
        }
        markdown += `\n`;
      }

      markdown += `---\n\n`;
    }

    return markdown;
  }

  buildTimeline(journeyNode) {
    let markdown = `## Timeline & SLA Breakdown\n\n`;

    markdown += `### Cumulative Timeline\n\n`;

    // Calculate cumulative SLA
    let totalHours = 0;
    const timeline = [];

    for (const phaseId of journeyNode.phases) {
      const phaseNode = this.graph.nodes[phaseId];

      for (const moduleId of phaseNode.modules) {
        const moduleNode = this.graph.nodes[moduleId];

        for (const atomId of moduleNode.atoms) {
          const atomNode = this.graph.nodes[atomId];
          totalHours += atomNode.sla_hours;

          timeline.push({
            title: atomNode.title,
            hours: atomNode.sla_hours,
            cumulative: totalHours
          });
        }
      }
    }

    markdown += `| Touchpoint | SLA (hours) | Cumulative (hours) | Cumulative (days) |\n`;
    markdown += `|------------|-------------|--------------------|-----------------|\n`;

    for (const item of timeline) {
      markdown += `| ${item.title} | ${item.hours} | ${item.cumulative} | ${(item.cumulative / 24).toFixed(1)} |\n`;
    }

    markdown += `\n**Total Journey SLA:** ${totalHours} hours (${(totalHours / 24).toFixed(1)} days)\n\n`;
    markdown += `**Target SLA:** ${journeyNode.sla_days} days\n`;

    if (totalHours / 24 <= journeyNode.sla_days) {
      markdown += `**Status:** ✅ Within target SLA\n\n`;
    } else {
      markdown += `**Status:** ⚠️  Exceeds target SLA by ${((totalHours / 24) - journeyNode.sla_days).toFixed(1)} days\n\n`;
    }

    markdown += `---\n\n`;
    return markdown;
  }

  buildMetrics(journeyNode) {
    return `## Success Metrics

### Journey-Level KPIs

- **Application Completion Rate:** Target > 80%
- **Time to Decision:** Target < ${journeyNode.sla_days} days
- **Customer Satisfaction (CSAT):** Target > 4.5/5
- **Net Promoter Score (NPS):** Target > 50
- **Pull-Through Rate:** Target > 75%
- **Closing Rate:** Target > 70%

### Quality Metrics

- **Post-Closing Audit Defect Rate:** Target < 2%
- **Investor Buyback Rate:** Target < 0.5%
- **Regulatory Compliance:** Target 100%
- **Document Accuracy:** Target > 98%

---

*Built with Customer Journey as Code*
*Framework: NASA-STD-2100-91 Atomic/Modular Documentation Principles*
`;
  }
}

// Run builder
const builder = new CustomerJourneyBuilder();
builder.build().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
