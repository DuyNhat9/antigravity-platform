from mcp.server import Server
import mcp.types as types
from typing import Optional
from .blackboard import blackboard
from ..models.task import TaskStatus

# Create an MCP Server
mcp_server = Server("antigravity-orchestrator")

@mcp_server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools for IDE agents."""
    return [
        types.Tool(
            name="fetch_next_task",
            description="Fetches the next available task assigned to you.",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role of the agent (e.g., Coder, Reviewer)"}
                },
                "required": ["role"]
            }
        ),
        types.Tool(
            name="submit_task_completion",
            description="Reports completion of a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task"},
                    "result": {"type": "string", "description": "The outcome or summary of the work"}
                },
                "required": ["task_id", "result"]
            }
        ),
        types.Tool(
            name="send_command",
            description="Allows an agent to assign a task to another agent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_role": {"type": "string", "description": "The role to receive the task"},
                    "description": {"type": "string", "description": "Details of the command"}
                },
                "required": ["target_role", "description"]
            }
        ),
        types.Tool(
            name="poll_tasks",
            description="Checks for available tasks for a specific role.",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role to poll for"}
                },
                "required": ["role"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handles tool calls from the IDE agent."""
    if name == "fetch_next_task":
        role = arguments.get("role")
        # Find the first in_progress or pending task for this role
        target_task = next((t for t in blackboard.tasks if t.role == role and t.status in [TaskStatus.IN_PROGRESS, TaskStatus.PENDING]), None)
        
        if target_task:
            return [types.TextContent(type="text", text=f"TASK_ID: {target_task.id}\nDESCRIPTION: {target_task.description}")]
        return [types.TextContent(type="text", text="No active tasks found for your role.")]

    elif name == "submit_task_completion":
        task_id = arguments.get("task_id")
        result = arguments.get("result")
        
        await blackboard.update_task_status(task_id, TaskStatus.DONE, result=result)
        await blackboard.add_log("System", f"Task {task_id} completed via MCP.")
        return [types.TextContent(type="text", text="Completion reported successfully.")]

    elif name == "send_command":
        target = arguments.get("target_role")
        desc = arguments.get("description")
        from ..models.task import Task
        import uuid
        
        new_task = Task(id=str(uuid.uuid4())[:8], description=desc, role=target)
        await blackboard.add_task(new_task)
        await blackboard.add_log("System", f"Command issued to {target}: {desc}")
        return [types.TextContent(type="text", text=f"Command registered with ID: {new_task.id}")]

    elif name == "poll_tasks":
        role = arguments.get("role")
        pending = [t for t in blackboard.tasks if t.role == role and t.status == TaskStatus.PENDING]
        
        if pending:
            return [types.TextContent(type="text", text=f"FOUND: {len(pending)} tasks.", data=pending[0].model_dump())]
        return [types.TextContent(type="text", text="NO_TASKS")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
