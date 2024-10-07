
from dataclasses import dataclass
# from typing import Any

from schema import Schema
from schema import Optional

# from spekulatio.exceptions import SpekulatioValidationError

@dataclass
class Rule:
    # action: Action
    patterns: list[str]

    @classmethod
    def from_dict(cls, data):
        """Create a Rule object from a data dictionary."""
        # validate
        schema = Schema({
            Optional("patterns", default=[]): list,
        })
        validated_data = schema.validate(data)
        patterns = validated_data['patterns']

        return cls(patterns=patterns)
