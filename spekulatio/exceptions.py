
class SpekulatioError(Exception):
    """Base class for Spekulatio exceptions."""

class SpekulatioInternalError(SpekulatioError):
    """Unexpected Spekulatio error."""

class SpekulatioInputError(SpekulatioError):
    """User input error."""

class SpekulatioValidationError(SpekulatioInputError):
    """User configuration error."""
