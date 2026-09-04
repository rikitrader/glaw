export interface PageAnchor { term: string; pages: number[]; }

/** Resolve anchors against form-feed-delimited extracted text. Pages are physical PDF pages, 1-based. */
export function resolvePdfAnchors(extractedText: string, terms: string[]): PageAnchor[] {
  const pages = extractedText.split('\f');
  return terms.map((term) => ({
    term,
    pages: pages.flatMap((page, index) => page.toLocaleLowerCase().includes(term.toLocaleLowerCase()) ? [index + 1] : [])
  }));
}

export function requirePdfAnchor(extractedText: string, term: string): number[] {
  const match = resolvePdfAnchors(extractedText, [term])[0];
  if (!match.pages.length) throw new Error(`citation anchor not found in extracted PDF: ${term}`);
  return match.pages;
}
