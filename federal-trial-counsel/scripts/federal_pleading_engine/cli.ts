/**
 * Federal Pleading Engine - CLI Interface
 *
 * Command-line interface for generating federal pleadings,
 * analyzing claims, and scoring MTD risk.
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  CaseInput,
  PleadingEngineOutput,
  ValidationResult,
  ValidationError,
} from './schema';
import { CLAIM_LIBRARY, getAllClaimKeys, isValidClaimKey } from './claim_library';
import { mapFactsToElements, autoSuggestClaims, generateFactGapReport } from './mapper';
import {
  generateClaimDraftOutput,
  generateComplaintSkeleton,
  analyzeJurisdiction,
} from './drafter';
import { calculateMTDRisk, generateDefenseMatrix, calculateSurvivalProbability } from './risk';

/**
 * Parse command line arguments
 */
function parseArgs(args: string[]): {
  input?: string;
  output?: string;
  claims?: string[];
  suggest?: boolean;
  help?: boolean;
  listClaims?: boolean;
  format?: 'json' | 'markdown';
} {
  const result: {
    input?: string;
    output?: string;
    claims?: string[];
    suggest?: boolean;
    help?: boolean;
    listClaims?: boolean;
    format?: 'json' | 'markdown';
  } = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--input':
      case '-i':
        result.input = args[++i];
        break;
      case '--out':
      case '-o':
        result.output = args[++i];
        break;
      case '--claims':
      case '-c':
        result.claims = args[++i]?.split(',')?.map(c => c.trim());
        break;
      case '--suggest':
      case '-s':
        result.suggest = true;
        break;
      case '--help':
      case '-h':
        result.help = true;
        break;
      case '--list':
      case '-l':
        result.listClaims = true;
        break;
      case '--format':
      case '-f':
        result.format = args[++i] as 'json' | 'markdown';
        break;
    }
  }

  return result;
}

/**
 * Display help message
 */
function showHelp(): void {
  console.log(`
Federal Pleading Engine CLI
============================

Usage: node cli.js [options]

Options:
  -i, --input <file>     Path to case input JSON file
  -o, --out <dir>        Output directory for generated files
  -c, --claims <list>    Comma-separated list of claim keys
  -s, --suggest          Auto-suggest claims based on facts
  -l, --list             List all available claim keys
  -f, --format <type>    Output format: json or markdown (default: markdown)
  -h, --help             Show this help message

Examples:
  node cli.js --input case.json --out ./output
  node cli.js --input case.json --suggest
  node cli.js --input case.json --claims "1983_fourth_excessive_force,1983_monell"
  node cli.js --list

`);
}

/**
 * List all available claims
 */
function listClaims(): void {
  console.log('\nAvailable Federal Causes of Action\n');
  console.log('===================================\n');

  const categories = new Set(Object.values(CLAIM_LIBRARY).map(c => c.category));

  for (const category of categories) {
    console.log(`\n## ${category.toUpperCase().replace(/_/g, ' ')}\n`);

    for (const [key, metadata] of Object.entries(CLAIM_LIBRARY)) {
      if (metadata.category === category) {
        console.log(`  ${key}`);
        console.log(`    ${metadata.name}`);
        console.log(`    Source: ${metadata.source}`);
        if (metadata.heightenedPleading) {
          console.log(`    [Rule 9(b) Required]`);
        }
        if (metadata.exhaustionRequired) {
          console.log(`    [Exhaustion: ${metadata.exhaustionType}]`);
        }
        console.log();
      }
    }
  }
}

/**
 * Validate case input
 */
function validateInput(input: unknown): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  if (!input || typeof input !== 'object') {
    errors.push({
      field: 'root',
      message: 'Input must be a valid object',
      severity: 'error',
    });
    return { valid: false, errors, warnings };
  }

  const caseInput = input as Record<string, unknown>;

  // Check required fields
  if (!caseInput.court) {
    errors.push({ field: 'court', message: 'Court information required', severity: 'error' });
  }

  if (!caseInput.parties) {
    errors.push({ field: 'parties', message: 'Parties information required', severity: 'error' });
  }

  if (!caseInput.facts || !Array.isArray(caseInput.facts) || caseInput.facts.length === 0) {
    errors.push({ field: 'facts', message: 'At least one fact entry required', severity: 'error' });
  }

  if (!caseInput.claims_requested) {
    warnings.push({
      field: 'claims_requested',
      message: 'No claims specified - will auto-suggest',
      severity: 'warning',
    });
  }

  // Validate claim keys if provided (unknown keys are hard errors, not warnings,
  // because downstream mapping silently degrades to empty output otherwise)
  if (caseInput.claims_requested && Array.isArray(caseInput.claims_requested)) {
    for (const claim of caseInput.claims_requested) {
      if (claim !== 'auto_suggest' && !isValidClaimKey(claim as string)) {
        errors.push({
          field: 'claims_requested',
          message: `Unknown claim key: ${claim}`,
          severity: 'error',
        });
      }
    }
  } else if (caseInput.claims_requested !== undefined
             && !Array.isArray(caseInput.claims_requested)) {
    errors.push({
      field: 'claims_requested',
      message: 'claims_requested must be an array of claim keys',
      severity: 'error',
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Format output as Markdown
 */
function formatAsMarkdown(output: PleadingEngineOutput): string {
  const lines: string[] = [];

  lines.push('# Federal Pleading Engine Output\n');
  lines.push(`Generated: ${output.generatedAt}\n`);

  // Jurisdiction Analysis
  lines.push('## Jurisdiction Analysis\n');
  lines.push(`**Basis:** ${output.jurisdictionAnalysis.subjectMatter.basis}`);
  lines.push(`**Analysis:** ${output.jurisdictionAnalysis.subjectMatter.analysis}`);
  lines.push(`**Venue:** ${output.jurisdictionAnalysis.venue.analysis}\n`);

  // Standing
  lines.push('### Standing');
  lines.push(`- Injury in Fact: ${output.jurisdictionAnalysis.standing.injuryInFact ? 'Yes' : 'No'}`);
  lines.push(`- Causation: ${output.jurisdictionAnalysis.standing.causation ? 'Yes' : 'No'}`);
  lines.push(`- Redressability: ${output.jurisdictionAnalysis.standing.redressability ? 'Yes' : 'No'}\n`);

  // Claim Outputs
  for (const claimOutput of output.claimOutputs) {
    lines.push(`---\n`);
    lines.push(`## Claim: ${claimOutput.claimKey}\n`);

    // Elements Table
    lines.push('### Elements\n');
    lines.push('| # | Element | Must Allege | Typical Evidence | Pitfalls |');
    lines.push('|---|---------|-------------|------------------|----------|');
    for (const row of claimOutput.elementsTable) {
      lines.push(`| ${row.number} | ${row.element} | ${row.mustAllege.substring(0, 50)}... | ${row.typicalEvidence.substring(0, 30)}... | ${row.pitfalls.substring(0, 30)}... |`);
    }
    lines.push('');

    // Preconditions
    if (claimOutput.preconditions.length > 0) {
      lines.push('### Preconditions\n');
      for (const pre of claimOutput.preconditions) {
        const status = pre.satisfied === true ? '[SATISFIED]' :
                       pre.satisfied === false ? '[NOT SATISFIED]' : '[UNKNOWN]';
        lines.push(`- ${status} ${pre.requirement}`);
      }
      lines.push('');
    }

    // Defenses
    lines.push('### Anticipated Defenses\n');
    for (const defense of claimOutput.defenses) {
      lines.push(`**${defense.type}** (Likelihood: ${defense.likelihood})`);
      lines.push(`- ${defense.description}`);
      lines.push(`- Counter: ${defense.counterArguments.join('; ')}\n`);
    }

    // Pleading Checklist
    lines.push('### Pleading Checklist\n');
    lines.push('| Element | Facts | Status |');
    lines.push('|---------|-------|--------|');
    for (const item of claimOutput.pleadingChecklist) {
      const facts = item.facts.length > 0 ? item.facts.join('; ').substring(0, 50) : '[MISSING]';
      lines.push(`| ${item.elementName} | ${facts}... | ${item.status.toUpperCase()} |`);
    }
    lines.push('');

    // Draft Count
    lines.push('### Draft Count\n');
    lines.push('```');
    lines.push(`                             COUNT ${claimOutput.draftCount.countNumber}`);
    lines.push(`                    ${claimOutput.draftCount.title.toUpperCase()}`);
    lines.push(`                   (${claimOutput.draftCount.statutoryCitation})\n`);
    lines.push(`     ${claimOutput.draftCount.incorporationParagraph}\n`);
    for (const allegation of claimOutput.draftCount.allegations) {
      lines.push(`     ${allegation.paragraphNumber}. ${allegation.text}\n`);
    }
    lines.push(`     ${claimOutput.draftCount.damagesParagraph}`);
    lines.push('```\n');

    // Fact Gaps
    if (claimOutput.factGaps.length > 0) {
      lines.push('### Fact Gaps\n');
      for (const gap of claimOutput.factGaps) {
        lines.push(`- **[${gap.priority.toUpperCase()}]** Element ${gap.elementNumber} (${gap.elementName}): ${gap.missingInfo}`);
        lines.push(`  - Sources: ${gap.suggestedSources.join(', ')}`);
      }
      lines.push('');
    }

    // MTD Risk
    lines.push('### MTD Risk Score\n');
    lines.push(`**Overall Score:** ${claimOutput.mtdRisk.overallScore}/100 (${claimOutput.mtdRisk.riskLevel.toUpperCase()})\n`);

    lines.push('**Risk Factors:**\n');
    for (const factor of claimOutput.mtdRisk.factors) {
      lines.push(`- ${factor.category}: ${factor.score}/100 - ${factor.issue}`);
    }
    lines.push('');

    if (claimOutput.mtdRisk.prioritizedFixes.length > 0) {
      lines.push('**Prioritized Fixes:**\n');
      for (const fix of claimOutput.mtdRisk.prioritizedFixes) {
        lines.push(`- ${fix}`);
      }
      lines.push('');
    }
  }

  // Complaint Skeleton
  lines.push('---\n');
  lines.push('## Complaint Skeleton\n');
  lines.push('```');
  lines.push(output.complaintSkeleton.caption);
  lines.push('\n                              COMPLAINT\n');
  lines.push(output.complaintSkeleton.partiesSection);
  lines.push('\n' + output.complaintSkeleton.jurisdictionSection);
  lines.push('\n' + output.complaintSkeleton.venueSection);
  lines.push('\n' + output.complaintSkeleton.generalAllegations.join('\n'));
  lines.push('\n                       CAUSES OF ACTION\n');
  // Counts already included in claim outputs
  lines.push('\n' + output.complaintSkeleton.prayerForRelief);
  if (output.complaintSkeleton.juryDemand) {
    lines.push('\n                           JURY DEMAND\n');
    lines.push('     Plaintiff demands a trial by jury on all issues so triable.');
  }
  lines.push('\n' + output.complaintSkeleton.certificateOfService);
  lines.push('```\n');

  // Consolidated Fact Gaps
  if (output.consolidatedFactGaps.length > 0) {
    lines.push('---\n');
    lines.push('## Consolidated Fact Gaps\n');
    for (const gap of output.consolidatedFactGaps) {
      lines.push(`- **[${gap.priority.toUpperCase()}]** ${gap.elementName}: ${gap.missingInfo}`);
    }
    lines.push('');
  }

  // Recommendations
  if (output.recommendations.length > 0) {
    lines.push('---\n');
    lines.push('## Recommendations\n');
    for (const rec of output.recommendations) {
      lines.push(`- ${rec}`);
    }
  }

  return lines.join('\n');
}

/**
 * Main CLI function
 */
async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    showHelp();
    process.exit(0);
  }

  if (args.listClaims) {
    listClaims();
    process.exit(0);
  }

  if (!args.input) {
    console.error('Error: Input file required. Use --input <file>');
    showHelp();
    process.exit(1);
  }

  // Read input file
  let caseInput: CaseInput;
  try {
    const inputPath = path.resolve(args.input);
    const inputContent = fs.readFileSync(inputPath, 'utf-8');
    caseInput = JSON.parse(inputContent);
  } catch (error) {
    console.error(`Error reading input file: ${(error as Error).message}`);
    process.exit(1);
  }

  // Validate input
  const validation = validateInput(caseInput);
  if (!validation.valid) {
    console.error('Validation Errors:');
    for (const error of validation.errors) {
      console.error(`  - ${error.field}: ${error.message}`);
    }
    process.exit(1);
  }

  if (validation.warnings.length > 0) {
    console.warn('Warnings:');
    for (const warning of validation.warnings) {
      console.warn(`  - ${warning.field}: ${warning.message}`);
    }
  }

  // Determine claims to process
  let claimsToProcess: string[] = [];

  if (args.suggest || caseInput.claims_requested[0] === 'auto_suggest') {
    console.log('\nAuto-suggesting claims based on facts...\n');
    const suggestions = autoSuggestClaims(caseInput);

    console.log('Suggested Claims:');
    console.log('=================\n');

    for (const suggestion of suggestions) {
      console.log(`${suggestion.claimKey} (Score: ${suggestion.matchScore})`);
      console.log(`  ${suggestion.claimName}`);
      if (suggestion.reasons.length > 0) {
        console.log(`  Reasons: ${suggestion.reasons.join('; ')}`);
      }
      if (suggestion.showstoppers.length > 0) {
        console.log(`  WARNINGS: ${suggestion.showstoppers.join('; ')}`);
      }
      console.log();
    }

    // Use top 3 viable claims
    claimsToProcess = suggestions
      .filter(s => s.showstoppers.length === 0)
      .slice(0, 3)
      .map(s => s.claimKey);

    if (claimsToProcess.length === 0) {
      console.warn('No viable claims found. Using top suggestion despite showstoppers.');
      claimsToProcess = suggestions.length > 0 ? [suggestions[0].claimKey] : [];
      if (claimsToProcess.length === 0) {
        console.error('No claims could be suggested from the provided facts.');
        process.exit(1);
      }
    }

  } else if (args.claims) {
    claimsToProcess = args.claims.filter(c => isValidClaimKey(c));
  } else if (caseInput.claims_requested && caseInput.claims_requested[0] !== 'auto_suggest') {
    claimsToProcess = (caseInput.claims_requested as string[]).filter(c => isValidClaimKey(c));
  }

  if (claimsToProcess.length === 0) {
    console.error('No valid claims to process');
    process.exit(1);
  }

  console.log(`\nProcessing claims: ${claimsToProcess.join(', ')}\n`);

  // Generate outputs
  const claimOutputs = claimsToProcess.map((claimKey, index) =>
    generateClaimDraftOutput(caseInput, claimKey, index + 1)
  );

  const jurisdictionAnalysis = analyzeJurisdiction(caseInput);
  const complaintSkeleton = generateComplaintSkeleton(caseInput, claimOutputs);
  const consolidatedFactGaps = generateFactGapReport(caseInput, claimsToProcess);
  const survival = calculateSurvivalProbability(caseInput, claimsToProcess);

  const output: PleadingEngineOutput = {
    caseInput,
    jurisdictionAnalysis,
    claimOutputs,
    complaintSkeleton,
    consolidatedFactGaps,
    recommendations: [
      survival.recommendation,
      ...survival.strengthBoosters.slice(0, 2),
      ...(survival.killRiskFlags.length > 0 ?
        [`Address critical issues: ${survival.killRiskFlags[0]}`] : []),
    ],
    generatedAt: new Date().toISOString(),
  };

  // Write output
  if (args.output) {
    const outDir = path.resolve(args.output);
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
    // Anchor outDir so derived paths (join + resolve) can't escape it
    const outDirReal = fs.realpathSync(outDir);

    const writeInside = (name: string, content: string): string => {
      const full = path.resolve(outDirReal, name);
      if (!full.startsWith(outDirReal + path.sep) && full !== outDirReal) {
        throw new Error(`Refusing to write outside output dir: ${name}`);
      }
      fs.writeFileSync(full, content);
      return full;
    };

    const jsonPath = writeInside('pleading_output.json', JSON.stringify(output, null, 2));
    console.log(`JSON output written to: ${jsonPath}`);

    const mdPath = writeInside('pleading_output.md', formatAsMarkdown(output));
    console.log(`Markdown output written to: ${mdPath}`);

    const complaintPath = writeInside('complaint_draft.md', formatComplaintDraft(output));
    console.log(`Complaint draft written to: ${complaintPath}`);

  } else {
    // Print to console
    if (args.format === 'json') {
      console.log(JSON.stringify(output, null, 2));
    } else {
      console.log(formatAsMarkdown(output));
    }
  }

  // Print summary
  console.log('\n========================================');
  console.log('             SUMMARY');
  console.log('========================================\n');
  console.log(`Claims Processed: ${claimsToProcess.length}`);
  console.log(`Fact Gaps: ${consolidatedFactGaps.length}`);
  console.log(`MTD Survival Probability: ${survival.mtdSurvival}%`);
  console.log(`SJ Survival Probability: ${survival.sjSurvival}%`);
  console.log(`Trial Likelihood: ${survival.trialLikelihood}%`);
  console.log(`\nRecommendation: ${survival.recommendation}`);
}

/**
 * Format complaint as standalone draft
 */
function formatComplaintDraft(output: PleadingEngineOutput): string {
  const lines: string[] = [];

  lines.push(output.complaintSkeleton.caption);
  lines.push('\n                              COMPLAINT\n');
  lines.push('     Plaintiff, by and through undersigned counsel, hereby sues Defendant(s) and alleges as follows:\n');
  lines.push('\n                         NATURE OF THE ACTION\n');
  const claimTitles = output.claimOutputs
    .map(c => c.draftCount.title)
    .filter(Boolean);
  const natureDesc =
    claimTitles.length === 0
      ? 'relief under federal law'
      : claimTitles.length === 1
      ? claimTitles[0]
      : claimTitles.slice(0, -1).join(', ') + ', and ' + claimTitles[claimTitles.length - 1];
  lines.push(`     1. This is an action for ${natureDesc}.\n`);
  lines.push(output.complaintSkeleton.partiesSection);
  lines.push('\n' + output.complaintSkeleton.jurisdictionSection);
  lines.push('\n' + output.complaintSkeleton.venueSection);
  lines.push('\n' + output.complaintSkeleton.generalAllegations.join('\n'));
  lines.push('\n                       CAUSES OF ACTION\n');

  for (const claimOutput of output.claimOutputs) {
    lines.push(`\n                             COUNT ${claimOutput.draftCount.countNumber}`);
    lines.push(`                    ${claimOutput.draftCount.title.toUpperCase()}`);
    lines.push(`                   (${claimOutput.draftCount.statutoryCitation})\n`);
    lines.push(`     ${claimOutput.draftCount.incorporationParagraph}\n`);
    for (const allegation of claimOutput.draftCount.allegations) {
      lines.push(`     ${allegation.paragraphNumber}. ${allegation.text}\n`);
    }
    lines.push(`     ${claimOutput.draftCount.damagesParagraph}\n`);
  }

  lines.push('\n' + output.complaintSkeleton.prayerForRelief);

  if (output.complaintSkeleton.juryDemand) {
    lines.push('\n                           JURY DEMAND\n');
    lines.push('     Plaintiff demands a trial by jury on all issues so triable.');
  }

  lines.push('\n                                        Respectfully submitted,\n');
  lines.push('                                        /s/ [ATTORNEY NAME]');
  lines.push('                                        [ATTORNEY NAME]');
  lines.push('                                        Florida Bar No. [NUMBER]');
  lines.push('                                        [FIRM NAME]');
  lines.push('                                        [ADDRESS]');
  lines.push('                                        [CITY], [STATE] [ZIP]');
  lines.push('                                        Telephone: [PHONE]');
  lines.push('                                        Email: [EMAIL]');
  lines.push('\n                                        Counsel for Plaintiff');

  lines.push('\n' + output.complaintSkeleton.certificateOfService);

  return lines.join('\n');
}

// Run CLI
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
