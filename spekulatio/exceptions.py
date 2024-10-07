
class SpekulatioError(Exception):
    """Base class for Spekulatio exceptions."""

class SpekulatioInternalError(SpekulatioError):
    """Unexpected Spekulatio error."""

class SpekulatioValidationError(SpekulatioError):
    """User configuration error."""
