
from datetime import datetime

def get_extra_globals():

    def _now(date_format: str = "%Y-%m-%d"):
        return datetime.now().strftime(date_format)
        
    return {
        '_now': _now,
        '_year': lambda: _now("%Y"),
    }
