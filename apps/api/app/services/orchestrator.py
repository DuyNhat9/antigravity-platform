import asyncio
from .blackboard import blackboard
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
        await blackboard.add_log(task.role, f"Starting task: {task.description}")
        await blackboard.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        # Simulate work
        await asyncio.sleep(2) 
        
        await blackboard.update_task_status(task.id, TaskStatus.DONE, result="Completed by Agent")
        await blackboard.add_log(task.role, f"Finished task: {task.id}")

# Singleton
orchestrator = Orchestrator()
