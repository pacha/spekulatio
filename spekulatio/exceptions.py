class SpekulatioBaseError(Exception):
    """Base class for Spekulatio exceptions."""

class SpekulatioInternalError(SpekulatioBaseError):
    """Unexpected error."""

class SpekulatioError(SpekulatioBaseError):
    """A known or expected error."""

class SpekulatioInputError(SpekulatioError):
    """User input error."""

class SpekulatioValidationError(SpekulatioInputError):
    """Wrong structure in one of the configuration files provided."""

class SpekulatioActionExecutionError(SpekulatioError):
    """Error found when executing an action."""
