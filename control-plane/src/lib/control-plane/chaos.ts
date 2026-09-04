export type FaultClass = "PROVIDER_TIMEOUT" | "PROVIDER_5XX" | "DUPLICATE_WEBHOOK" | "STALE_RECEIPT" | "QUEUE_DELAY" | "REGION_FENCE" | "MALFORMED_TOOL_OUTPUT";
export type FaultDisposition = "RETRY" | "DEAD_LETTER" | "RECONCILE" | "FAIL_CLOSED" | "ESCALATE";

export function dispositionForFault(fault: FaultClass): FaultDisposition {
  switch (fault) {
    case "PROVIDER_TIMEOUT":
    case "PROVIDER_5XX":
    case "QUEUE_DELAY": return "RETRY";
    case "DUPLICATE_WEBHOOK": return "RECONCILE";
    case "STALE_RECEIPT": return "RECONCILE";
    case "REGION_FENCE": return "FAIL_CLOSED";
    case "MALFORMED_TOOL_OUTPUT": return "DEAD_LETTER";
  }
}
