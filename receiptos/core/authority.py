class AuthorityViolation(ValueError):
    """Raised when authority is anything other than literal False."""



def enforce_authority(authority):
    """
    Runtime constitutional guard.

    Only literal False is admissible. Any other value is a violation.
    No coercion, no casting, no alternate authority path.
    """
    if authority is not False:
        raise AuthorityViolation(f"authority must be False, got {authority!r}")
    return True
