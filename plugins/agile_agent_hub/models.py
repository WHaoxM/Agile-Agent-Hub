from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Task:
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    raw_text: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)
