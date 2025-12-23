from .blackboard import blackboard
from ..models.task import Task
import uuid
import asyncio

class Commander:
    async def plan(self, user_request: str):
        await blackboard.add_log("Commander", f"Planning task for: {user_request}")
        await asyncio.sleep(0.5) # Simulate thinking
        
        # Mock Planner Logic
        tasks = [
            Task(id="task_1", description="Analyze Requirements", role="Architect"),
            Task(id="task_2", description="Setup Project Structure", role="Executive", dependencies=["task_1"]),
            Task(id="task_3", description="Implement Core Logic", role="Coder", dependencies=["task_2"]),
            Task(id="task_4", description="Review Implementation", role="Reviewer", dependencies=["task_3"])
        ]
        
        for t in tasks:
            await blackboard.add_task(t)
            
        await blackboard.add_log("Commander", "Planning complete. 4 tasks created.")

# Singleton
commander = Commander()
