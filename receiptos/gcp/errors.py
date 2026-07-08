class GCPPacketValidationError(ValueError):
    """Raised when a GCP read-only audit packet is not admissible."""


class DisallowedCommandError(GCPPacketValidationError):
    """Raised when a gcloud command is outside the read-only membrane."""


class SchemaValidationError(GCPPacketValidationError):
    """Raised when a packet fails schema validation."""


class AuthorityViolationError(GCPPacketValidationError):
    """Raised when authority is anything other than literal False."""
