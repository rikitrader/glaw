import type { JsonValue } from '../types.ts';
export function clone<T extends JsonValue>(value:T):T{return JSON.parse(JSON.stringify(value)) as T;}
export function getPath(value:JsonValue,path:string):JsonValue|undefined{return path.split('.').reduce<JsonValue|undefined>((current,key)=>{if(current&&typeof current==='object')return Array.isArray(current)?current[Number(key)] as JsonValue:(current as Record<string,JsonValue>)[key];return undefined;},value);}
export function stableStringify(value:JsonValue):string{if(value===null||typeof value!=='object')return JSON.stringify(value);if(Array.isArray(value))return `[${value.map(stableStringify).join(',')}]`;return `{${Object.keys(value).sort().map((key)=>`${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;}
