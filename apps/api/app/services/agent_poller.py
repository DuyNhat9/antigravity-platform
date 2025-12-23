import asyncio
import httpx
import sys
import os

# Fix path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.automation import automation
from app.services.blackboard import blackboard
from app.models.task import TaskStatus

# Configuration
API_BASE_URL = "http://localhost:8000"
POLL_INTERVAL = 5  # Seconds

async def poll_mcp_for_tasks(role: str):
    """
    Background loop that polls the MCP server for tasks.
    """
    print(f"🕵️ Agent Poller started for role: {role}")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # We check the blackboard directly since we are in the same project context
                if blackboard.auto_trigger_enabled:
                    pending_tasks = [t for t in blackboard.tasks if t.role == role and t.status == TaskStatus.PENDING]
                    
                    if pending_tasks:
                        task = pending_tasks[0]
                        print(f"🎯 TASK DETECTED: {task.id} - {task.description}")
                        
                        # Trigger UI
                        await automation.trigger_agent(role, task.description)
                        
                        # Mark as In Progress immediately to avoid double-triggering
                        await blackboard.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                        print(f"🚀 {role} triggered autonomously.")
                else:
                    # Optional: print or log that we are waiting for auto-trigger to be enabled
                    pass

            except Exception as e:
                print(f"❌ Poller Error: {e}")
            
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "Coder"
    asyncio.run(poll_mcp_for_tasks(role))
