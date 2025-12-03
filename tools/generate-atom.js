#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class AtomGenerator {
  constructor() {
    this.outputDir = path.join(__dirname, '..', 'journey-components', 'atoms');
  }

  async generate() {
    console.log('🤖 Customer Journey Atom Generator');
    console.log('═'.repeat(70));

    const description = process.argv[2];
    const category = process.argv[3] || 'auto';

    if (!description) {
      this.showUsage();
      return;
    }

    console.log(`\n📝 Generating atom from description...`);
    console.log(`   Description: "${description}"`);
    console.log(`   Category: ${category}\n`);

    const atom = await this.generateAtom(description, category);

    // Determine output directory based on atom type
    let subdir = '';
    switch (atom.data.atom_type) {
      case 'customer-action':
        subdir = 'customer-actions';
        break;
      case 'back-office-action':
        subdir = 'back-office-actions';
        break;
      case 'system-action':
        subdir = 'system-actions';
        break;
      default:
        subdir = 'other';
    }

    const targetDir = path.join(this.outputDir, subdir);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const filename = `${atom.data.id}.yaml`;
    const filepath = path.join(targetDir, filename);

    fs.writeFileSync(filepath, atom.yaml, 'utf8');

    console.log(`✅ Atom generated successfully!`);
    console.log(`📁 File: ${filepath}`);
    console.log(`🆔 ID: ${atom.data.id}`);
    console.log(`📋 Title: ${atom.data.title}`);
    console.log(`\n⚠️  NOTE: This is a template. Please review and customize:`);
    console.log(`   • Verify all fields are accurate`);
    console.log(`   • Add detailed steps`);
    console.log(`   • Specify regulatory references`);
    console.log(`   • Set appropriate SLA`);
    console.log(`   • Add to graph/customer-journey-graph.json\n`);
  }

  async generateAtom(description, category) {
    // Auto-detect actor and atom type from description
    const descLower = description.toLowerCase();

    let actor = 'unknown';
    let atomType = 'unknown';
    let subtype = 'unknown';

    // Detect actor
    if (descLower.includes('customer') || descLower.includes('borrower')) {
      actor = 'customer';
      atomType = 'customer-action';
      subtype = 'cust';
    } else if (descLower.includes('processor')) {
      actor = 'processor';
      atomType = 'back-office-action';
      subtype = 'bo';
    } else if (descLower.includes('underwriter')) {
      actor = 'underwriter';
      atomType = 'back-office-action';
      subtype = 'bo';
    } else if (descLower.includes('system') || descLower.includes('automated')) {
      actor = 'system';
      atomType = 'system-action';
      subtype = 'sys';
    } else if (descLower.includes('loan officer') || descLower.includes('lo ')) {
      actor = 'loan_officer';
      atomType = 'back-office-action';
      subtype = 'bo';
    } else if (descLower.includes('closer')) {
      actor = 'closer';
      atomType = 'back-office-action';
      subtype = 'bo';
    } else {
      // Default to back-office
      actor = 'processor';
      atomType = 'back-office-action';
      subtype = 'bo';
    }

    // Generate ID from description
    const words = description
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .split(/\s+/)
      .filter(w => !['the', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in'].includes(w))
      .slice(0, 5)
      .join('-');

    const atomId = `atom-${subtype}-${words}`;

    // Generate title (capitalize first letter of each word)
    const title = description
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

    // Determine default SLA based on type
    let defaultSLA = 24;
    if (atomType === 'system-action') {
      defaultSLA = 0.25;
    } else if (atomType === 'customer-action') {
      defaultSLA = 48;
    }

    // Determine customer visibility
    const customerVisible = atomType === 'customer-action' ||
                            descLower.includes('notif') ||
                            descLower.includes('decision') ||
                            descLower.includes('approval');

    const frontStage = customerVisible;

    // Build atom data structure
    const atomData = {
      id: atomId,
      type: 'atom',
      title: title,
      version: '1.0.0',
      atom_type: atomType,
      actor: actor,
      front_stage: frontStage,
      customer_visible: customerVisible,
      sla_hours: defaultSLA,
      criticality: 'medium',
      description: `${description}\n\nTODO: Expand this description with full details.`,
      preconditions: [
        'TODO: Define preconditions'
      ],
      steps: [
        {
          step: 1,
          action: 'TODO: Define step 1'
        },
        {
          step: 2,
          action: 'TODO: Define step 2'
        }
      ],
      postconditions: [
        'TODO: Define postconditions'
      ],
      data_outputs: [
        'TODO: List data outputs'
      ],
      regulatory_refs: [
        'TODO: Add relevant regulations (TRID, ECOA, ATR/QM, etc.)'
      ],
      risk_category: 'medium',
      compliance_notes: 'TODO: Add compliance notes',
      customer_sentiment_impact: 'neutral',
      customer_effort_score: 'medium',
      touchpoint_importance: 'medium',
      dependencies: {
        depends_on: [],
        enables: [],
        triggers: []
      },
      success_metrics: [
        'TODO: Define success metrics'
      ],
      notes: 'Generated by atom-generator. Please review and customize all fields.'
    };

    const atomYaml = yaml.dump(atomData, {
      indent: 2,
      lineWidth: 100,
      noRefs: true
    });

    // Add YAML front matter delimiter
    const atomYamlWithDelimiter = `---\n${atomYaml}`;

    return {
      yaml: atomYamlWithDelimiter,
      data: atomData
    };
  }

  showUsage() {
    console.log('\nUsage: node generate-atom.js "<description>" [category]\n');
    console.log('Examples:');
    console.log('  node generate-atom.js "Customer uploads bank statements"');
    console.log('  node generate-atom.js "Processor calculates debt-to-income ratio"');
    console.log('  node generate-atom.js "System sends approval notification to customer"');
    console.log('  node generate-atom.js "Underwriter reviews appraisal report"\n');
    console.log('The generator will automatically detect:');
    console.log('  • Actor (customer, processor, underwriter, system, etc.)');
    console.log('  • Atom type (customer-action, back-office-action, system-action)');
    console.log('  • Appropriate SLA defaults');
    console.log('  • Customer visibility\n');
    console.log('After generation, you must:');
    console.log('  1. Review and customize the generated YAML');
    console.log('  2. Add the atom to graph/customer-journey-graph.json');
    console.log('  3. Create appropriate edges to connect it to other atoms\n');
  }
}

// Run generator
const generator = new AtomGenerator();
generator.generate().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
