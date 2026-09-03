export interface SandboxPolicy { network:'DENY'|'ALLOWLIST'; filesystem:'EPISODE_ONLY'; secrets:'NONE'; maxSeconds:number; maxMemoryMb:number; allowedTools:string[]; }
export const DEFAULT_SANDBOX_POLICY:SandboxPolicy={network:'DENY',filesystem:'EPISODE_ONLY',secrets:'NONE',maxSeconds:300,maxMemoryMb:512,allowedTools:[]};
export function validateActionTool(tool:string,policy:SandboxPolicy):void{if(!policy.allowedTools.includes(tool))throw new Error(`tool is not allowed by sandbox policy: ${tool}`);}
