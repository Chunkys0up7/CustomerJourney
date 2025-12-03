#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class GraphValidator {
  constructor() {
    this.graphPath = path.join(__dirname, '..', 'graph', 'customer-journey-graph.json');
    this.graph = null;
    this.errors = [];
    this.warnings = [];
  }

  async validate() {
    console.log('🔍 Customer Journey Graph Validator');
    console.log('═'.repeat(70));

    try {
      this.loadGraph();

      console.log('\n📋 Running validation checks...\n');

      // Run all validation checks
      this.validateSchema();
      this.validateReferences();
      this.validateConnectivity();
      this.validateCircularDependencies();
      this.validateSLAs();
      this.validateRegulatory();

      // Display results
      this.displayResults();

      if (this.errors.length > 0) {
        process.exit(1);
      }

    } catch (error) {
      console.error('❌ Validation failed:', error.message);
      process.exit(1);
    }
  }

  loadGraph() {
    try {
      const graphData = fs.readFileSync(this.graphPath, 'utf8');
      this.graph = JSON.parse(graphData);
      console.log('✓ Graph loaded successfully');
    } catch (error) {
      throw new Error(`Failed to load graph: ${error.message}`);
    }
  }

  validateSchema() {
    console.log('Validating schema...');

    // Check required top-level fields
    const requiredFields = ['metadata', 'nodes', 'edges'];
    for (const field of requiredFields) {
      if (!this.graph[field]) {
        this.errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate metadata
    if (this.graph.metadata) {
      if (!this.graph.metadata.schema_version) {
        this.warnings.push('Metadata missing schema_version');
      }
      if (!this.graph.metadata.stats) {
        this.warnings.push('Metadata missing stats');
      }
    }

    // Validate nodes
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (!node.id) {
        this.errors.push(`Node ${nodeId} missing 'id' field`);
      }
      if (node.id !== nodeId) {
        this.errors.push(`Node ${nodeId}: id field '${node.id}' does not match key`);
      }
      if (!node.type) {
        this.errors.push(`Node ${nodeId} missing 'type' field`);
      }
      if (!node.title) {
        this.errors.push(`Node ${nodeId} missing 'title' field`);
      }

      // Type-specific validation
      if (node.type === 'atom') {
        if (!node.actor) {
          this.errors.push(`Atom ${nodeId} missing 'actor' field`);
        }
        if (!node.atom_type) {
          this.errors.push(`Atom ${nodeId} missing 'atom_type' field`);
        }
        if (typeof node.customer_visible !== 'boolean') {
          this.errors.push(`Atom ${nodeId} missing or invalid 'customer_visible' field`);
        }
        if (typeof node.sla_hours !== 'number') {
          this.errors.push(`Atom ${nodeId} missing or invalid 'sla_hours' field`);
        }
      }

      if (node.type === 'module') {
        if (!node.atoms || !Array.isArray(node.atoms)) {
          this.errors.push(`Module ${nodeId} missing or invalid 'atoms' array`);
        }
      }

      if (node.type === 'phase') {
        if (!node.modules || !Array.isArray(node.modules)) {
          this.errors.push(`Phase ${nodeId} missing or invalid 'modules' array`);
        }
      }

      if (node.type === 'journey') {
        if (!node.phases || !Array.isArray(node.phases)) {
          this.errors.push(`Journey ${nodeId} missing or invalid 'phases' array`);
        }
      }
    }

    // Validate edges
    if (!Array.isArray(this.graph.edges)) {
      this.errors.push('Edges must be an array');
    } else {
      for (let i = 0; i < this.graph.edges.length; i++) {
        const edge = this.graph.edges[i];
        if (!edge.source) {
          this.errors.push(`Edge ${i} missing 'source' field`);
        }
        if (!edge.target) {
          this.errors.push(`Edge ${i} missing 'target' field`);
        }
        if (!edge.type) {
          this.errors.push(`Edge ${i} missing 'type' field`);
        }
      }
    }

    console.log(`  ${this.errors.length === 0 ? '✓' : '✗'} Schema validation complete`);
  }

  validateReferences() {
    console.log('Validating references...');

    // Check that all edge sources and targets exist
    for (const edge of this.graph.edges) {
      if (!this.graph.nodes[edge.source]) {
        this.errors.push(`Edge references non-existent source: ${edge.source}`);
      }
      if (!this.graph.nodes[edge.target]) {
        this.errors.push(`Edge references non-existent target: ${edge.target}`);
      }
    }

    // Check that module atoms exist
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'module' && node.atoms) {
        for (const atomId of node.atoms) {
          if (!this.graph.nodes[atomId]) {
            this.errors.push(`Module ${nodeId} references non-existent atom: ${atomId}`);
          } else if (this.graph.nodes[atomId].type !== 'atom') {
            this.errors.push(`Module ${nodeId} references ${atomId} which is not an atom`);
          }
        }
      }

      if (node.type === 'phase' && node.modules) {
        for (const moduleId of node.modules) {
          if (!this.graph.nodes[moduleId]) {
            this.errors.push(`Phase ${nodeId} references non-existent module: ${moduleId}`);
          } else if (this.graph.nodes[moduleId].type !== 'module') {
            this.errors.push(`Phase ${nodeId} references ${moduleId} which is not a module`);
          }
        }
      }

      if (node.type === 'journey' && node.phases) {
        for (const phaseId of node.phases) {
          if (!this.graph.nodes[phaseId]) {
            this.errors.push(`Journey ${nodeId} references non-existent phase: ${phaseId}`);
          } else if (this.graph.nodes[phaseId].type !== 'phase') {
            this.errors.push(`Journey ${nodeId} references ${phaseId} which is not a phase`);
          }
        }
      }
    }

    console.log(`  ${this.errors.length === 0 ? '✓' : '✗'} Reference validation complete`);
  }

  validateConnectivity() {
    console.log('Validating connectivity...');

    // Find orphaned nodes (nodes not referenced by any edge or parent)
    const referencedNodes = new Set();

    // Add all edge targets and sources
    for (const edge of this.graph.edges) {
      referencedNodes.add(edge.source);
      referencedNodes.add(edge.target);
    }

    // Add all atoms in modules, modules in phases, phases in journeys
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'module' && node.atoms) {
        node.atoms.forEach(atomId => referencedNodes.add(atomId));
      }
      if (node.type === 'phase' && node.modules) {
        node.modules.forEach(moduleId => referencedNodes.add(moduleId));
      }
      if (node.type === 'journey' && node.phases) {
        node.phases.forEach(phaseId => referencedNodes.add(phaseId));
      }
    }

    // Check for orphaned atoms (atoms not in any module)
    const orphanedAtoms = [];
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'atom' && !referencedNodes.has(nodeId)) {
        orphanedAtoms.push(nodeId);
      }
    }

    if (orphanedAtoms.length > 0) {
      this.warnings.push(`Found ${orphanedAtoms.length} orphaned atoms: ${orphanedAtoms.join(', ')}`);
    }

    console.log(`  ${orphanedAtoms.length === 0 ? '✓' : '⚠'} Connectivity validation complete`);
  }

  validateCircularDependencies() {
    console.log('Validating circular dependencies...');

    // Build adjacency list
    const adjacency = new Map();
    for (const [nodeId] of Object.entries(this.graph.nodes)) {
      adjacency.set(nodeId, []);
    }
    for (const edge of this.graph.edges) {
      if (adjacency.has(edge.source)) {
        adjacency.get(edge.source).push(edge.target);
      }
    }

    // DFS to detect cycles
    const visited = new Set();
    const recursionStack = new Set();

    const hasCycle = (node, path = []) => {
      if (recursionStack.has(node)) {
        this.errors.push(`Circular dependency detected: ${path.join(' → ')} → ${node}`);
        return true;
      }

      if (visited.has(node)) {
        return false;
      }

      visited.add(node);
      recursionStack.add(node);
      path.push(node);

      const neighbors = adjacency.get(node) || [];
      for (const neighbor of neighbors) {
        if (hasCycle(neighbor, [...path])) {
          return true;
        }
      }

      recursionStack.delete(node);
      return false;
    };

    for (const [nodeId] of Object.entries(this.graph.nodes)) {
      if (!visited.has(nodeId)) {
        hasCycle(nodeId);
      }
    }

    console.log(`  ${this.errors.length === 0 ? '✓' : '✗'} Circular dependency check complete`);
  }

  validateSLAs() {
    console.log('Validating SLAs...');

    // Check that all atoms have SLA hours
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'atom') {
        if (typeof node.sla_hours !== 'number' || node.sla_hours < 0) {
          this.errors.push(`Atom ${nodeId} has invalid sla_hours: ${node.sla_hours}`);
        }
      }
    }

    // Validate module SLAs match sum of atoms
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'module' && node.atoms) {
        let calculatedSLA = 0;
        for (const atomId of node.atoms) {
          const atom = this.graph.nodes[atomId];
          if (atom && typeof atom.sla_hours === 'number') {
            calculatedSLA += atom.sla_hours;
          }
        }

        if (node.sla_hours && Math.abs(node.sla_hours - calculatedSLA) > 0.1) {
          this.warnings.push(`Module ${nodeId} SLA (${node.sla_hours}h) doesn't match sum of atoms (${calculatedSLA}h)`);
        }
      }
    }

    console.log(`  ${this.errors.length === 0 ? '✓' : '✗'} SLA validation complete`);
  }

  validateRegulatory() {
    console.log('Validating regulatory compliance...');

    // Check that customer-visible atoms have regulatory references
    for (const [nodeId, node] of Object.entries(this.graph.nodes)) {
      if (node.type === 'atom' && node.customer_visible) {
        if (!node.regulatory_refs || node.regulatory_refs.length === 0) {
          this.warnings.push(`Customer-visible atom ${nodeId} missing regulatory_refs`);
        }
      }
    }

    console.log(`  ✓ Regulatory validation complete`);
  }

  displayResults() {
    console.log('\n' + '═'.repeat(70));
    console.log('📊 VALIDATION RESULTS');
    console.log('═'.repeat(70));

    console.log(`\n📈 Graph Statistics:`);
    console.log(`   Nodes: ${Object.keys(this.graph.nodes).length}`);
    console.log(`   Edges: ${this.graph.edges.length}`);

    const nodeTypes = {};
    for (const node of Object.values(this.graph.nodes)) {
      nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1;
    }

    console.log(`\n   By Type:`);
    for (const [type, count] of Object.entries(nodeTypes)) {
      console.log(`     ${type}: ${count}`);
    }

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log(`\n✅ Graph is valid! No errors or warnings.`);
    } else {
      if (this.errors.length > 0) {
        console.log(`\n❌ Errors (${this.errors.length}):`);
        for (const error of this.errors) {
          console.log(`   • ${error}`);
        }
      }

      if (this.warnings.length > 0) {
        console.log(`\n⚠️  Warnings (${this.warnings.length}):`);
        for (const warning of this.warnings) {
          console.log(`   • ${warning}`);
        }
      }

      if (this.errors.length === 0) {
        console.log(`\n✅ Graph is valid (with warnings).`);
      } else {
        console.log(`\n❌ Graph validation failed.`);
      }
    }

    console.log('\n' + '═'.repeat(70) + '\n');
  }
}

// Run validator
const validator = new GraphValidator();
validator.validate().catch(error => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
