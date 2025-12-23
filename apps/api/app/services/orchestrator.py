import asyncio
from .blackboard import blackboard
from .automation import automation
from ..models.task import TaskStatus
from ..models.agent import AgentStatus
from ..core.socket import sio

class Orchestrator:
    def __init__(self):
        self._running = False

    async def start(self):
        self._running = True
        asyncio.create_task(self._loop())
        await blackboard.add_log("Orchestrator", "Service started.")

    async def stop(self):
        self._running = False
        await blackboard.add_log("Orchestrator", "Service stopped.")

    async def _loop(self):
        while self._running:
            # 1. Find executable tasks
            executable_tasks = self._get_executable_tasks()
            
            # 2. Assign to workers (Mock)
            for task in executable_tasks:
                asyncio.create_task(self._execute_task(task))
            
            await asyncio.sleep(1)

    def _get_executable_tasks(self):
        # Allow checking synchronous list from async loop (simple for now)
        done_ids = {t.id for t in blackboard.tasks if t.status == TaskStatus.DONE}
        return [
            t for t in blackboard.tasks 
            if t.status == TaskStatus.PENDING 
            and all(dep in done_ids for dep in t.dependencies)
        ]

    async def _execute_task(self, task):
        # In Phase 5, if 'Autonomous Mode' is handled by individual agent pollers,
        # the orchestrator acts more as a tracker/coordinator.
        
        await blackboard.add_log(task.role, f"Switching to active status: {task.description}")
        await blackboard.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        try:
            # If we are using local development with UI Triggers:
            await self._dispatch_to_worker(task)
            await blackboard.add_log(task.role, f"Mandate transmitted to IDE. Awaiting report...")
        except Exception as e:
            await blackboard.update_task_status(task.id, TaskStatus.ERROR, result=str(e))
            await blackboard.add_log(task.role, f"ERROR: System breach or failure: {str(e)}")

    async def _dispatch_to_worker(self, task):
        # Find an available agent for this role
        target_agent = next((a for a in blackboard.agents if a.role == task.role and a.status == AgentStatus.IDLE), None)
        
        if target_agent:
            await blackboard.add_log("Orchestrator", f"Dispatching mission to targeted Node: {target_agent.id}")
            await blackboard.update_agent_status(target_agent.id, AgentStatus.BUSY, task_id=task.id)
            # Emit specifically to the agent's room
            await sio.emit("task_assigned", {"task": task.model_dump()}, room=target_agent.id)
        
        # We still perform UI trigger for the main IDE window as a parallel/fallback
        await automation.trigger_agent(task.role, task.description)
        
        return f"Awaiting mission report from IDE Agent ({task.role})..."

# Singleton
orchestrator = Orchestrator()
