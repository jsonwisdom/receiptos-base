export type ReplayStrategy = 'linear' | 'fork-aware' | 'doctrinal';

export interface ReceiptState {
  stateRoot: string;
  authority: false;
  noFakeGreen: true;
}

export interface AttestedEvent {
  uid: string;
  schemaUid: string;
  txHash?: string;
  eventHash: string;
  payload: unknown;
  authority: false;
}

export interface DoctrineInvariant {
  id: string;
  description: string;
  required: true;
}

export interface ReplayContext {
  initialState: ReceiptState;
  events: AttestedEvent[];
  strategy: ReplayStrategy;
  invariants: DoctrineInvariant[];
}

export interface ReplayResult {
  stateRoot: string;
  eventCount: number;
  strategy: ReplayStrategy;
  authority: false;
  noFakeGreen: true;
  verifiedReplay: false;
  invariantCount: number;
}
