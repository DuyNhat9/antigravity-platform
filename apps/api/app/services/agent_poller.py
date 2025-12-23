import asyncio
import httpx
import sys
import os
from automation import automation

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
                # In a real MCP setup, we would use the MCP SDK to call 'poll_tasks'.
                # For this implementation, we simulate it via a direct internal-only API call 
                # or by direct access to services if running in the same process.
                # However, to be 'True MCP', we'll simulate the tool logic here.
                
                # We'll use a hidden endpoint or just check the blackboard if we had shared access.
                # To match the user's plan of 'polling over MCP', we'll use the API.
                
                # Check for 'Auto-Trigger' flag in environment or global state
                # (Assuming Orchestrator or a global setting enables this)
                
                response = await client.get(f"{API_BASE_URL}/") # Simple health check for now
                if response.status_code == 200:
                    # In this demo version, since we're in the same backend context, 
                    # we can import the blackboard directly to check.
                    from app.services.blackboard import blackboard
                    from app.models.task import TaskStatus
                    
                    pending_tasks = [t for t in blackboard.tasks if t.role == role and t.status == TaskStatus.PENDING]
                    
                    if pending_tasks:
                        task = pending_tasks[0]
                        print(f"🎯 TASK DETECTED: {task.id} - {task.description}")
                        
                        # Trigger UI
                        await automation.trigger_agent(role, task.description)
                        
                        # Mark as In Progress immediately to avoid double-triggering
                        await blackboard.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                        print(f"🚀 {role} triggered autonomously.")

            except Exception as e:
                print(f"❌ Poller Error: {e}")
            
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "Coder"
    asyncio.run(poll_mcp_for_tasks(role))
