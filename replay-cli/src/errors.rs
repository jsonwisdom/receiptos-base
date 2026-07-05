#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ReplayExit {
    Success = 0,
    TranscriptIdMismatch = 19,
    InvalidReceipt = 20,
    InvalidEnvelope = 21,
    DomainMismatch = 30,
    HashMismatch = 31,
    StepTraceMismatch = 32,
    UnsupportedProtocol = 41,
    IoError = 42,
    WasmExecutionFailed = 43,
}
