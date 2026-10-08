from dataclasses import dataclass
from typing import Optional

@dataclass
class SessionContext:
    email: str
    employee_id: str
    token: Optional[str] = None
