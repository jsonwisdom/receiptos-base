import { computeInterpretation, WireReceipt } from "../lib/interpretation/policies";

export function trustScoreAdapter(receipt: WireReceipt) {
  return computeInterpretation(receipt, "trust-score-v1");
}

export function riskAdapter(receipt: WireReceipt) {
  return computeInterpretation(receipt, "risk-v1");
}
