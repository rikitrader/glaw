export interface SourceAdapter<TInput,TOutput> { readonly name:string; readonly version:string; canHandle(input:TInput):boolean; parse(input:TInput):Promise<TOutput>; }
export interface OcrAdapter extends SourceAdapter<{mimeType:string; bytes:Uint8Array},{text:string; confidence:number}> {}
export interface XactimateAdapter extends SourceAdapter<{format:'ESX'|'XML'|'CSV'|'PDF'|'JSON'; payload:unknown},unknown> {}
export interface LegalSourceAdapter extends SourceAdapter<{jurisdiction:string; query:string},unknown> {}
export function unavailableAdapter<TInput,TOutput>(name:string):SourceAdapter<TInput,TOutput> { return {name,version:'UNAVAILABLE',canHandle:()=>false,parse:async()=>{throw new Error(`${name}: provider adapter is unavailable; source is required`);}}; }
