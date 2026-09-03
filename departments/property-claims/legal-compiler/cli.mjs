#!/usr/bin/env node
import { SUPPORTED_JURISDICTIONS } from './jurisdictions/registry.ts';
import { generateBenchmarkCatalog } from './benchmarks/generator.ts';
import { buildRemediationMatrix, summarizeRemediation } from './remediation/matrix.ts';
import { getJurisdictionStatus } from './core/status.ts';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
const [command,...args]=process.argv.slice(2);
if(command==='jurisdictions') console.log(JSON.stringify({count:SUPPORTED_JURISDICTIONS.length,jurisdictions:SUPPORTED_JURISDICTIONS.map((item)=>item.code)},null,2));
else if(command==='benchmark-catalog') console.log(JSON.stringify({count:generateBenchmarkCatalog(args[0]).length,status:'RESEARCH_REQUIRED',humanReviewRequired:true},null,2));
else if(command==='matrix') { const items=buildRemediationMatrix(); console.log(JSON.stringify({count:items.length,byReason:summarizeRemediation(items),items},null,2)); }
else if(command==='status') { const code=args[0]??'FL'; const root=join(new URL('.',import.meta.url).pathname,'jurisdictions'); console.log(JSON.stringify(getJurisdictionStatus(root,code),null,2)); }
else if(command==='research') { console.log(JSON.stringify({status:'RESEARCH_PIPELINE_READY',jurisdiction:args[0]??'ALL',issue:args[1]??'ALL',message:'Use an authorized source provider to retrieve primary authority; no rules are activated by discovery alone.'},null,2)); }
else if(command==='verify') { const code=args[0]??'FL'; const root=join(new URL('.',import.meta.url).pathname,'jurisdictions'); const status=getJurisdictionStatus(root,code); console.log(JSON.stringify(status,null,2)); if(status.status!=='COMPLETE_VERIFIED') process.exitCode=1; }
else if(command==='help'||!command) console.log('Usage: glaw legal jurisdictions | benchmark-catalog [YYYY-MM-DD] | matrix | status [STATE] | research [STATE] [ISSUE] | verify [STATE]');
else { console.error(`Unknown command: ${command}`); process.exitCode=2; }
