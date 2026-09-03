import type { AuthorityRecord, DiscoveryAudit, DiscoveryDeadline, DiscoveryObject, Matter, ProceduralEvent } from '../types';

const authorityMap: Record<string, string> = {
  response: 'Fla. R. Civ. P. 1.340, 1.350, or 1.370 — exact rule depends on discovery kind [AUTHORITY REQUIRED]',
  compel: 'Fla. R. Civ. P. 1.380 [AUTHORITY REQUIRED]',
  scope: 'Fla. R. Civ. P. 1.280 [AUTHORITY REQUIRED]',
  execution: 'Fla. R. Civ. P. 1.560 [AUTHORITY REQUIRED]',
};

function hasEvent(events: ProceduralEvent[], ...types: string[]): ProceduralEvent | undefined {
  return events.find((event) => types.includes(event.eventType.toUpperCase()));
}

function authorityRule(kind: DiscoveryObject['kind']): string { switch (kind) { case 'INTERROGATORY': return '1.340'; case 'REQUEST_FOR_PRODUCTION': return '1.350'; case 'REQUEST_FOR_ADMISSION': return '1.370'; case 'DEPOSITION': return '1.310'; case 'ORDER': return '1.200'; case 'RESPONSE': return '1.340'; default: return '1.280'; } }
function hasVerifiedAuthority(kind: DiscoveryObject['kind'], authorities: AuthorityRecord[], matterId?: string): boolean { const rule = authorityRule(kind); return authorities.some((authority) => authority.status === 'VERIFIED' && (!authority.matterId || authority.matterId === matterId) && (`${authority.name} ${authority.citation} ${authority.proposition ?? ''}`).includes(rule)); }
function hasVerifiedRule(rule: string, authorities: AuthorityRecord[], matterId?: string): boolean { return authorities.some((authority) => authority.status === 'VERIFIED' && (!authority.matterId || authority.matterId === matterId) && (`${authority.name} ${authority.citation} ${authority.proposition ?? ''}`).includes(rule)); }
function governingRule(kind: DiscoveryObject['kind'], verified = false): string { const suffix = verified ? '' : ' [AUTHORITY REQUIRED]'; switch (kind) { case 'INTERROGATORY': return `Fla. R. Civ. P. 1.340${suffix}`; case 'REQUEST_FOR_PRODUCTION': return `Fla. R. Civ. P. 1.350${suffix}`; case 'REQUEST_FOR_ADMISSION': return `Fla. R. Civ. P. 1.370${suffix}`; case 'DEPOSITION': return `Fla. R. Civ. P. 1.310${suffix}`; case 'ORDER': return `Fla. R. Civ. P. 1.200 and applicable order${suffix}`; case 'RESPONSE': return `Fla. R. Civ. P. 1.340, 1.350, or 1.370${suffix}`; default: return `Fla. R. Civ. P. 1.280 and applicable discovery rule${suffix}`; } }

const writtenDiscoveryDays: Partial<Record<DiscoveryObject['kind'], number>> = { INTERROGATORY: 30, REQUEST_FOR_PRODUCTION: 30, REQUEST_FOR_ADMISSION: 30 };

function addCalendarDays(date: string, days: number): string | undefined {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return undefined;
  const value = new Date(`${date}T00:00:00.000Z`);
  if (Number.isNaN(value.getTime())) return undefined;
  value.setUTCDate(value.getUTCDate() + days);
  return value.toISOString().slice(0, 10);
}

/**
 * Produces a transparent candidate only. It deliberately does not apply
 * service-method extensions, court orders, holidays, or stipulations because
 * those facts are not stored on a DiscoveryObject.
 */
export function calculateDiscoveryDeadline(object: DiscoveryObject): DiscoveryDeadline {
  const rule = governingRule(object.kind);
  const days = writtenDiscoveryDays[object.kind];
  if (!days) return { status: 'NOT_APPLICABLE', rule, serviceDate: object.servedAt, responseDue: object.responseDue, explanation: 'No default written-response interval is calculated for this discovery kind.', warnings: ['DATE_VERIFICATION_REQUIRED: inspect the notice, order, deposition setting, and applicable procedure.'] };
  if (!object.servedAt) return { status: 'DATE_VERIFICATION_REQUIRED', rule, responseDue: object.responseDue, explanation: 'A service date is required before even a candidate date can be computed.', warnings: ['DATE_VERIFICATION_REQUIRED: service date, service method, extensions, and court orders are missing.'] };
  const candidateDueDate = addCalendarDays(object.servedAt, days);
  if (!candidateDueDate) return { status: 'DATE_VERIFICATION_REQUIRED', rule, serviceDate: object.servedAt, responseDue: object.responseDue, explanation: 'The stored service date is not a valid ISO calendar date.', warnings: ['DATE_VERIFICATION_REQUIRED: verify the certificate of service and date format.'] };
  return { status: 'CANDIDATE', rule, serviceDate: object.servedAt, responseDue: object.responseDue, candidateDueDate, explanation: `Candidate only: ${days} calendar days added to the recorded service date. This is not a verified legal due date.`, warnings: ['DATE_VERIFICATION_REQUIRED: confirm service method, any initial-pleading exception, extensions, stipulations, court orders, weekends/holidays, and the current rule text.'] };
}

export function buildDiscoveryAudit(matter: Matter | null, objects: DiscoveryObject[], events: ProceduralEvent[], authorities: AuthorityRecord[] = []): DiscoveryAudit {
  const tenantId = matter?.tenantId ?? objects[0]?.tenantId ?? events[0]?.tenantId ?? 'UNKNOWN';
  const matterId = matter?.matterId ?? objects[0]?.matterId ?? events[0]?.matterId ?? 'UNKNOWN';
  const recordedFinalJudgment = hasEvent(events, 'FINAL_JUDGMENT', 'JUDGMENT_ENTERED');
  const finalJudgment = recordedFinalJudgment?.status === 'VERIFIED' ? recordedFinalJudgment : undefined;
  const posture: DiscoveryAudit['posture'] = finalJudgment ? 'POST_JUDGMENT' : recordedFinalJudgment ? 'UNKNOWN' : matter ? 'PRE_JUDGMENT' : 'UNKNOWN';
  const findings: DiscoveryAudit['findings'] = [];
  const warnings: string[] = [];

  findings.push({
    requirement: 'Matter identity and procedural posture',
    authority: posture === 'POST_JUDGMENT' ? `Fla. R. Civ. P. 1.560${hasVerifiedRule('1.560', authorities, matter?.matterId) ? '' : ' [AUTHORITY REQUIRED]'}` : 'Record classification [RECORD REQUIRED]',
    status: matter ? 'SATISFIED' : 'RECORD_REQUIRED',
    evidenceIds: matter ? [`matter:${matter.matterId}`] : [],
    notes: matter ? `Matter ${matter.matterId} is classified as ${posture}.` : 'No matter record was supplied.',
    requestedRemedy: matter ? undefined : 'Load the operative case and court-order record before motion analysis.',
  });

  if (objects.length === 0) {
    findings.push({ requirement: 'Underlying discovery requests', authority: authorityMap.response!, status: 'RECORD_REQUIRED', evidenceIds: [], notes: 'No discovery objects are available for request-by-request analysis.', requestedRemedy: 'Ingest the requests, responses, objections, and production record.' });
  }

  const meetAndConfer = hasEvent(events, 'MEET_AND_CONFER', 'GOOD_FAITH_CONFERENCE', 'DISCOVERY_CONFERENCE');
  const motions = objects.filter((object) => object.kind === 'MOTION_TO_COMPEL');
  if (motions.length > 0) {
    const missingMotionRecord = motions.flatMap((motion) => [!motion.exactText ? `motion ${motion.id}: exact motion text` : '', !motion.servedAt ? `motion ${motion.id}: service date` : ''].filter(Boolean));
    findings.push({ requirement: 'Motion-to-compel record and service', authority: `Fla. R. Civ. P. 1.380${hasVerifiedRule('1.380', authorities, matter?.matterId) ? '' : ' [AUTHORITY REQUIRED]'}`, status: missingMotionRecord.length === 0 ? 'SATISFIED' : 'RECORD_REQUIRED', evidenceIds: motions.filter((motion) => motion.exactText && motion.servedAt).map((motion) => `discovery:${motion.id}`), notes: missingMotionRecord.length === 0 ? 'Motion text and service date are recorded; verify the filed motion and certificate.' : 'The system will not infer the filed motion or service record.', requestedRemedy: missingMotionRecord.length === 0 ? 'Verify the motion, certificate, and hearing notice.' : `Obtain ${missingMotionRecord.join('; ')}.` });
  }
  if (motions.length > 0) {
    findings.push({
      requirement: 'Good-faith attempt to resolve a discovery dispute',
      authority: `Fla. R. Civ. P. 1.380${hasVerifiedRule('1.380', authorities, matter?.matterId) ? '' : ' [AUTHORITY REQUIRED]'}`,
      status: meetAndConfer ? 'SATISFIED' : 'RECORD_REQUIRED',
      evidenceIds: meetAndConfer ? [`event:${meetAndConfer.id}`] : [],
      notes: meetAndConfer ? 'A conference event is recorded; its contents and certification still require human review.' : 'No conference event is recorded. This does not prove that no conference occurred.',
      requestedRemedy: meetAndConfer ? 'Verify the correspondence and motion certification.' : 'Obtain the meet-and-confer correspondence and certification.',
    });
  }

  const requestFindings = objects.filter((object) => object.kind !== 'MOTION_TO_COMPEL').map((object): DiscoveryAudit['requestFindings'][number] => {
    const missingRecord: string[] = [];
    const itemFindings: string[] = [];
    if (!object.exactText) missingRecord.push('exact request text');
    if (!object.servedAt) missingRecord.push('service date');
    if (!object.responseDue) missingRecord.push('response due date and service-method calculation');
    if (!object.responseText && !object.objectionText && object.productionStatus === 'UNKNOWN') missingRecord.push('response, objection, and production record');
    const verifiedRule = hasVerifiedAuthority(object.kind, authorities, matter?.matterId);
    const deadline = calculateDiscoveryDeadline(object);
    if (deadline.status === 'DATE_VERIFICATION_REQUIRED') itemFindings.push(...deadline.warnings);
    if (object.responseDue && deadline.candidateDueDate && object.responseDue !== deadline.candidateDueDate) itemFindings.push(`Stored responseDue ${object.responseDue} differs from the unverified candidate ${deadline.candidateDueDate}; resolve from the certificate, service method, order, or stipulation.`);
    if (missingRecord.length) return { discoveryId: object.id, requestNumber: object.requestNumber, governingRule: governingRule(object.kind, verifiedRule), deadline, result: 'RECORD_REQUIRED', findings: ['The system will not infer the request, deadline, response, or production status.', ...deadline.warnings], missingRecord };
    if (object.productionStatus === 'PRODUCED' || object.productionStatus === 'NO_RESPONSIVE_DOCUMENTS') itemFindings.push('The stored production status indicates a completed response position; compare the actual materials before conceding compliance.');
    if (object.productionStatus === 'PARTIAL' || object.productionStatus === 'PRIVILEGE_REVIEW') itemFindings.push('The stored status indicates a possible supplementation, narrowing, privilege, or protection issue.');
    if (object.productionStatus === 'NOT_PRODUCED') itemFindings.push('The stored status indicates non-production; determine whether the response was due and whether an objection or agreement explains it.');
    const result: DiscoveryAudit['requestFindings'][number]['result'] = object.productionStatus === 'PARTIAL' || object.productionStatus === 'PRIVILEGE_REVIEW' ? 'SUPPLEMENT' : object.productionStatus === 'PRODUCED' ? 'CONCEDE' : object.productionStatus === 'NO_RESPONSIVE_DOCUMENTS' ? 'NO_RESPONSIVE_DOCUMENTS' : object.productionStatus === 'NOT_PRODUCED' ? 'OBJECT' : 'RECORD_REQUIRED';
    return { discoveryId: object.id, requestNumber: object.requestNumber, governingRule: governingRule(object.kind, verifiedRule), deadline, result, findings: itemFindings, missingRecord };
  });

  if (posture === 'POST_JUDGMENT') {
    warnings.push('Post-judgment discovery must be separately tested for a genuine aid-of-execution purpose; the audit does not infer that predicate from a label.');
    if (!finalJudgment) warnings.push(recordedFinalJudgment ? 'A final-judgment event exists but is not verified; execution posture remains unverified.' : 'Final judgment event is absent; posture cannot be verified.');
  }
  if (objects.some((object) => object.status !== 'VERIFIED')) warnings.push('One or more discovery objects are not verified; this audit is a lead for human review, not a filing fact.');

  const requiresRecord = posture === 'UNKNOWN' || findings.some((finding) => finding.status === 'RECORD_REQUIRED') || requestFindings.some((finding) => finding.missingRecord.length > 0);
  const requiresAuthority = findings.some((finding) => finding.authority.includes('[AUTHORITY REQUIRED]')) || requestFindings.some((finding) => finding.governingRule.includes('[AUTHORITY REQUIRED]'));
  const status: DiscoveryAudit['status'] = requiresRecord ? 'REQUIRES_RECORD' : requiresAuthority ? 'REQUIRES_AUTHORITY' : 'READY_FOR_HUMAN_REVIEW';
  return { tenantId, matterId, posture, status, findings, requestFindings, warnings, humanReview: 'REQUIRED', createdAt: new Date().toISOString() };
}
