#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class CustomerJourneyImpactAnalyzer {
  constructor() {
    this.graphPath = path.join(__dirname, '..', 'graph', 'customer-journey-graph.json');
    this.graph = null;
  }

  loadGraph() {
    try {
      const graphData = fs.readFileSync(this.graphPath, 'utf8');
      this.graph = JSON.parse(graphData);
    } catch (error) {
      throw new Error(`Failed to load graph: ${error.message}`);
    }
  }

  // Main analysis method
  analyzeAtomChange(atomId, changeType = 'modify') {
    console.log(`\n🔍 Analyzing impact of ${changeType} on: ${atomId}`);
    console.log('═'.repeat(70));

    const atomNode = this.graph.nodes[atomId];
    if (!atomNode) {
      throw new Error(`Atom ${atomId} not found in graph`);
    }

    const impacts = {
      atom_id: atomId,
      atom_title: atomNode.title,
      change_type: changeType,
      all_downstream: [],
      customer_facing: [],
      back_office: [],
      system_impacts: [],
      regulatory: [],
      phases_affected: new Set(),
      modules_affected: new Set(),
      journeys_affected: new Set(),
      total_sla_impact_hours: 0,
      risk_level: '',
      recommendations: []
    };

    // 1. Find all downstream atoms using graph traversal (DFS)
    this.traverseDownstream(atomId, impacts.all_downstream);

    console.log(`\n📊 Impact Summary:`);
    console.log(`   Direct downstream touchpoints: ${impacts.all_downstream.length}`);

    // 2. Categorize impacts
    for (const downstreamId of impacts.all_downstream) {
      const node = this.graph.nodes[downstreamId];

      if (node.type === 'atom') {
        if (node.customer_visible) {
          impacts.customer_facing.push({
            id: downstreamId,
            title: node.title,
            actor: node.actor,
            sla_hours: node.sla_hours,
            regulatory_refs: node.regulatory_refs || []
          });
        }

        if (!node.customer_visible && node.atom_type === 'back-office-action') {
          impacts.back_office.push({
            id: downstreamId,
            title: node.title,
            actor: node.actor
          });
        }

        if (node.atom_type === 'system-action') {
          impacts.system_impacts.push({
            id: downstreamId,
            title: node.title
          });
        }

        if (node.regulatory_refs && node.regulatory_refs.length > 0) {
          impacts.regulatory.push({
            id: downstreamId,
            title: node.title,
            refs: node.regulatory_refs
          });
        }

        impacts.total_sla_impact_hours += node.sla_hours || 0;
      }

      if (node.type === 'module') {
        impacts.modules_affected.add(downstreamId);
      }

      if (node.type === 'phase') {
        impacts.phases_affected.add(downstreamId);
      }

      if (node.type === 'journey') {
        impacts.journeys_affected.add(downstreamId);
      }
    }

    // 3. Calculate risk level
    impacts.risk_level = this.calculateRiskLevel(impacts);

    // 4. Generate recommendations
    impacts.recommendations = this.generateRecommendations(impacts, changeType);

    // 5. Display detailed report
    this.displayImpactReport(impacts);

    return impacts;
  }

  traverseDownstream(nodeId, visited = []) {
    // Find all edges where this node is the source
    const outgoingEdges = this.graph.edges.filter(edge => edge.source === nodeId);

    for (const edge of outgoingEdges) {
      if (!visited.includes(edge.target)) {
        visited.push(edge.target);
        this.traverseDownstream(edge.target, visited);
      }
    }
  }

  calculateRiskLevel(impacts) {
    let riskScore = 0;

    // Customer-facing impacts are high risk
    riskScore += impacts.customer_facing.length * 5;

    // Regulatory impacts are critical
    riskScore += impacts.regulatory.length * 10;

    // SLA impacts
    if (impacts.total_sla_impact_hours > 48) {
      riskScore += 15;
    } else if (impacts.total_sla_impact_hours > 24) {
      riskScore += 10;
    } else if (impacts.total_sla_impact_hours > 8) {
      riskScore += 5;
    }

    // System impacts
    riskScore += impacts.system_impacts.length * 3;

    // Multiple phases affected
    riskScore += impacts.phases_affected.size * 7;

    // Determine risk level
    if (riskScore >= 50) {
      return 'CRITICAL';
    } else if (riskScore >= 30) {
      return 'HIGH';
    } else if (riskScore >= 15) {
      return 'MEDIUM';
    } else {
      return 'LOW';
    }
  }

  generateRecommendations(impacts, changeType) {
    const recommendations = [];

    // Customer-facing recommendations
    if (impacts.customer_facing.length > 0) {
      recommendations.push({
        category: 'Customer Experience',
        priority: 'HIGH',
        action: `Test customer-facing touchpoints (${impacts.customer_facing.length} affected)`,
        details: 'Conduct usability testing and gather customer feedback before deployment'
      });
    }

    // Regulatory recommendations
    if (impacts.regulatory.length > 0) {
      recommendations.push({
        category: 'Compliance',
        priority: 'CRITICAL',
        action: 'Legal/Compliance review required',
        details: `${impacts.regulatory.length} touchpoints with regulatory requirements affected. Review TRID, ECOA, and ATR/QM implications.`
      });
    }

    // SLA recommendations
    if (impacts.total_sla_impact_hours > 24) {
      recommendations.push({
        category: 'Timeline',
        priority: 'HIGH',
        action: 'Review SLA commitments',
        details: `${(impacts.total_sla_impact_hours / 24).toFixed(1)} days of downstream SLA affected. May impact closing timeline.`
      });
    }

    // System recommendations
    if (impacts.system_impacts.length > 0) {
      recommendations.push({
        category: 'Technology',
        priority: 'MEDIUM',
        action: 'IT system testing required',
        details: `${impacts.system_impacts.length} system integrations affected. Test AUS, LOS, and document management systems.`
      });
    }

    // Phase-level recommendations
    if (impacts.phases_affected.size > 1) {
      recommendations.push({
        category: 'Process',
        priority: 'HIGH',
        action: 'Cross-phase coordination needed',
        details: `Multiple phases affected. Coordinate with all department heads before implementation.`
      });
    }

    // Change-type specific recommendations
    if (changeType === 'delete') {
      recommendations.push({
        category: 'Risk Management',
        priority: 'CRITICAL',
        action: 'Verify no orphaned dependencies',
        details: 'Removing this atom may break downstream workflows. Ensure all dependencies are updated or rerouted.'
      });
    }

    // Always recommend testing
    recommendations.push({
      category: 'Quality Assurance',
      priority: 'HIGH',
      action: 'End-to-end journey testing',
      details: 'Test complete journey from application to closing to verify no broken workflows.'
    });

    return recommendations;
  }

  displayImpactReport(impacts) {
    console.log(`\n${'═'.repeat(70)}`);
    console.log(`📋 IMPACT ANALYSIS REPORT`);
    console.log(`${'═'.repeat(70)}`);

    console.log(`\n🎯 Atom: ${impacts.atom_title}`);
    console.log(`   Change Type: ${impacts.change_type.toUpperCase()}`);
    console.log(`   Risk Level: ${this.getRiskEmoji(impacts.risk_level)} ${impacts.risk_level}`);

    console.log(`\n📈 Downstream Impact:`);
    console.log(`   Total touchpoints affected: ${impacts.all_downstream.length}`);
    console.log(`   Customer-facing impacts: ${impacts.customer_facing.length}`);
    console.log(`   Back-office impacts: ${impacts.back_office.length}`);
    console.log(`   System integrations: ${impacts.system_impacts.length}`);
    console.log(`   Regulatory touchpoints: ${impacts.regulatory.length}`);

    console.log(`\n⏱️  Timeline Impact:`);
    console.log(`   Total downstream SLA: ${impacts.total_sla_impact_hours} hours (${(impacts.total_sla_impact_hours / 24).toFixed(1)} days)`);

    console.log(`\n🏗️  Structural Impact:`);
    console.log(`   Modules affected: ${impacts.modules_affected.size}`);
    console.log(`   Phases affected: ${impacts.phases_affected.size}`);
    console.log(`   Journeys affected: ${impacts.journeys_affected.size}`);

    if (impacts.customer_facing.length > 0) {
      console.log(`\n👥 Customer-Facing Touchpoints Affected:`);
      for (const item of impacts.customer_facing) {
        console.log(`   • ${item.title} (${item.actor}, ${item.sla_hours}h SLA)`);
        if (item.regulatory_refs.length > 0) {
          console.log(`     📋 Regulatory: ${item.regulatory_refs.join(', ')}`);
        }
      }
    }

    if (impacts.regulatory.length > 0) {
      console.log(`\n⚖️  Regulatory Compliance Impact:`);
      const uniqueRefs = new Set();
      for (const item of impacts.regulatory) {
        item.refs.forEach(ref => uniqueRefs.add(ref));
      }
      console.log(`   Affected regulations: ${Array.from(uniqueRefs).join(', ')}`);
    }

    console.log(`\n💡 Recommendations:`);
    for (const rec of impacts.recommendations) {
      const priorityEmoji = rec.priority === 'CRITICAL' ? '🔴' : rec.priority === 'HIGH' ? '🟠' : '🟡';
      console.log(`\n   ${priorityEmoji} ${rec.category} [${rec.priority}]:`);
      console.log(`      ${rec.action}`);
      console.log(`      ${rec.details}`);
    }

    console.log(`\n${'═'.repeat(70)}\n`);
  }

  getRiskEmoji(riskLevel) {
    switch (riskLevel) {
      case 'CRITICAL': return '🔴';
      case 'HIGH': return '🟠';
      case 'MEDIUM': return '🟡';
      case 'LOW': return '🟢';
      default: return '⚪';
    }
  }

  // Interactive CLI
  async run() {
    console.log('🔍 Customer Journey Impact Analyzer');
    console.log('═'.repeat(70));

    this.loadGraph();

    // Get atom ID from command line or show menu
    const atomId = process.argv[2];

    if (!atomId) {
      console.log('\nUsage: node impact-analysis.js <atom-id> [change-type]\n');
      console.log('Available atoms:');

      const atoms = Object.keys(this.graph.nodes).filter(
        id => this.graph.nodes[id].type === 'atom'
      );

      for (const id of atoms) {
        const node = this.graph.nodes[id];
        console.log(`  • ${id} - ${node.title}`);
      }

      console.log('\nChange types: modify (default), delete, update-sla\n');
      console.log('Example: node impact-analysis.js atom-cust-income-w2-upload modify\n');
      return;
    }

    const changeType = process.argv[3] || 'modify';

    this.analyzeAtomChange(atomId, changeType);
  }
}

// Run analyzer
const analyzer = new CustomerJourneyImpactAnalyzer();
analyzer.run().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
