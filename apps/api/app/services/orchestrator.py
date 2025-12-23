import asyncio
from .blackboard import blackboard
from .automation import automation
from ..models.task import TaskStatus

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
        await blackboard.add_log(task.role, f"Switching to active status: {task.description}")
        await blackboard.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        try:
            # Dispatch to real agent (Triggers UI)
            await self._dispatch_to_worker(task)
            # We DON'T set status to DONE here. 
            # The IDE agent will call submit_task_completion via MCP to mark it DONE.
            await blackboard.add_log(task.role, f"Mandate transmitted to IDE. Awaiting report...")
        except Exception as e:
            await blackboard.update_task_status(task.id, TaskStatus.ERROR, result=str(e))
            await blackboard.add_log(task.role, f"ERROR: System breach or failure: {str(e)}")

    async def _dispatch_to_worker(self, task):
        # 1. Real UI Trigger (AppleScript)
        await automation.trigger_agent(task.role, task.description)
        
        # 2. Waiting for MCP callback (Task will be updated to DONE via mcp_server.py)
        # For now, we return a message that we are waiting for the IDE agent.
        return f"Awaiting mission report from IDE Agent ({task.role})..."

# Singleton
orchestrator = Orchestrator()
