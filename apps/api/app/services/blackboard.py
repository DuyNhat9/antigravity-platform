from typing import List, Dict, Optional
from ..models.task import Task, TaskStatus
from ..models.agent import Agent, AgentStatus
from ..core.socket import sio
import uuid

class Blackboard:
    def __init__(self):
        self.tasks: List[Task] = []
        self.agents: List[Agent] = []
        self.logs: Dict[str, List[str]] = {}
        self.auto_trigger_enabled = False

    async def set_auto_trigger(self, enabled: bool):
        self.auto_trigger_enabled = enabled
        await sio.emit("config_updated", {"auto_trigger_enabled": enabled})
        await self.add_log("System", f"Auto-Trigger Mode: {'ENABLED' if enabled else 'DISABLED'}")

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

    async def register_agent(self, role: str) -> Agent:
        agent_id = f"{role.lower()}_{str(uuid.uuid4())[:8]}"
        agent = Agent(id=agent_id, role=role, window_id=f"win_{agent_id}")
        self.agents.append(agent)
        await sio.emit("agent_added", agent.model_dump())
        await self.add_log("System", f"Agent Registry: {role} ({agent_id}) online.")
        return agent

    async def update_agent_status(self, agent_id: str, status: AgentStatus, task_id: Optional[str] = None):
        for agent in self.agents:
            if agent.id == agent_id:
                agent.status = status
                agent.current_task_id = task_id
                await sio.emit("agent_updated", agent.model_dump())
                break

# Singleton Instance
blackboard = Blackboard()
