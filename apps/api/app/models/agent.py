from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class Agent(BaseModel):
    id: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    window_id: Optional[str] = None
    current_task_id: Optional[str] = None
