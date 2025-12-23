from typing import List, Dict, Optional
from ..models.task import Task, TaskStatus
from ..core.socket import sio

class Blackboard:
    def __init__(self):
        self.tasks: List[Task] = []
        self.logs: Dict[str, List[str]] = {}

    async def add_task(self, task: Task):
        self.tasks.append(task)
        await sio.emit("task_added", task.model_dump())

    async def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[str] = None):
        updated_task = None
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                if result:
                    task.result = result
                updated_task = task
                break
        
        if updated_task:
            await sio.emit("task_updated", updated_task.model_dump())

    async def add_log(self, agent_name: str, message: str):
        if agent_name not in self.logs:
            self.logs[agent_name] = []
        
        log_entry = {"agent": agent_name, "message": message}
        self.logs[agent_name].append(message)
        await sio.emit("agent_log", log_entry)

# Singleton Instance
blackboard = Blackboard()
