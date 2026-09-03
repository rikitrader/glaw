export interface RetrievalResponse { ok: boolean; status: number; headers: { get(name: string): string | null }; arrayBuffer(): Promise<ArrayBuffer>; }
export interface RetrievedSource { url: string; status: 'FOUND' | 'RESTRICTED' | 'VERIFIED'; http_status: number; content_type: string; bytes: number; is_pdf: boolean; is_html: boolean; is_json: boolean; is_csv: boolean; reason: string; body: Uint8Array | null; }

const accessErrorMarkers = ['<title>error', '<title>404', '404</title>', '<h1>404', 'page not found', '/errors/404', 'page-name="404"', 'this page can\'t be displayed', 'access denied', 'request blocked', 'captcha', 'incident id', 'cloudflare ray id', 'automated queries', '_incapsula_resource', 'incapsula_resource', 'noindex,nofollow'];

export async function retrievePublicSource(url: string, fetchImpl: (url: string) => Promise<RetrievalResponse>): Promise<RetrievedSource> {
  if (!url.startsWith('https://')) return { url, status: 'RESTRICTED', http_status: 0, content_type: '', bytes: 0, is_pdf: false, is_html: false, is_json: false, is_csv: false, reason: 'Only HTTPS public sources are eligible.', body: null };
  let response: RetrievalResponse;
  try { response = await fetchImpl(url); } catch (error) {
    return { url, status: 'RESTRICTED', http_status: 0, content_type: '', bytes: 0, is_pdf: false, is_html: false, is_json: false, is_csv: false, reason: `Retrieval failed before an HTTP response: ${error instanceof Error ? error.message : String(error)}`, body: null };
  }
  const contentType = response.headers.get('content-type') ?? ''; const body = new Uint8Array(await response.arrayBuffer()); const fullText = new TextDecoder().decode(body); const text = fullText.slice(0, 512).toLowerCase(); const isPdf = new TextDecoder().decode(body.subarray(0, 5)) === '%PDF-' || contentType.includes('application/pdf'); const isHtml = contentType.includes('text/html') || text.includes('<html') || text.includes('<!doctype html'); const isJson = contentType.includes('application/json') || /^[\s]*[\[{]/.test(fullText); const isCsv = contentType.includes('text/csv') || contentType.includes('application/csv');
  if (!response.ok) return { url, status: 'RESTRICTED', http_status: response.status, content_type: contentType, bytes: body.byteLength, is_pdf: isPdf, is_html: isHtml, is_json: isJson, is_csv: isCsv, reason: `HTTP ${response.status}; not admitted to verified corpus.`, body: null };
  if (!isPdf && !isHtml && !isJson && !isCsv) return { url, status: 'RESTRICTED', http_status: response.status, content_type: contentType, bytes: body.byteLength, is_pdf: false, is_html: false, is_json: false, is_csv: false, reason: 'Unsupported content type; source cannot be admitted as evidence.', body: null };
  if (isHtml && accessErrorMarkers.some((marker) => text.includes(marker))) return { url, status: 'RESTRICTED', http_status: response.status, content_type: contentType, bytes: body.byteLength, is_pdf: false, is_html: true, is_json: false, is_csv: false, reason: 'Provider returned an access, anti-bot, or error HTML page; body not admitted.', body: null };
  if (isJson) {
    try { JSON.parse(fullText); } catch { return { url, status: 'RESTRICTED', http_status: response.status, content_type: contentType, bytes: body.byteLength, is_pdf: false, is_html: false, is_json: true, is_csv: false, reason: 'Provider returned malformed JSON; body not admitted.', body: null }; }
  }
  const reason = isPdf ? 'Public PDF retrieved; local hash and citation extraction still required.' : isJson ? 'Public JSON retrieved; local hash, schema, and observation verification still required.' : isCsv ? 'Public CSV retrieved; local hash, schema, and observation verification still required.' : 'Public HTML retrieved; page/section citation extraction still required.';
  return { url, status: 'FOUND', http_status: response.status, content_type: contentType, bytes: body.byteLength, is_pdf: isPdf, is_html: isHtml, is_json: isJson, is_csv: isCsv, reason, body };
}
