from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ERROR = "error"

class Task(BaseModel):
    id: str
    description: str
    role: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = []
    result: Optional[str] = None
