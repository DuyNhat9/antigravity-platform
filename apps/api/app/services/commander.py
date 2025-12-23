from .blackboard import blackboard
from .llm import llm_service
from ..models.task import Task
import uuid
import asyncio
import json

class Commander:
    async def plan(self, user_request: str):
        await blackboard.add_log("Commander", f"Neural engine analyzing: {user_request}")
        
        prompt = f"""
        You are the Commander of an AI Agent Swarm. 
        Analyze the user request and decompose it into a JSON list of tasks.
        
        Request: "{user_request}"
        
        Rules:
        1. Roles must be one of: Architect, Coder, Reviewer, Executive.
        2. Assign dependencies logically (e.g., Coder depends on Architect).
        3. Keep task descriptions clear and actionable.
        
        Output format:
        [
            {{"id": "task_id", "description": "task description", "role": "Architect", "dependencies": []}},
            ...
        ]
        """
        
        try:
            raw_json = await llm_service.generate_json(prompt)
            if not raw_json:
                await blackboard.add_log("Commander", "Error: LLM service unavailable. Falling back to mock planner.")
                tasks_data = self._mock_planner(user_request)
            else:
                tasks_data = json.loads(raw_json)
                await blackboard.add_log("Commander", f"Successfully generated {len(tasks_data)} tasks via Gemini.")
        except Exception as e:
            await blackboard.add_log("Commander", f"Planning failed: {str(e)}. Falling back.")
            tasks_data = self._mock_planner(user_request)
        
        for task in tasks_data:
            await blackboard.add_task(Task(**task))
            
        await blackboard.add_log("Commander", "Mission deployment sequence complete.")

    def _mock_planner(self, user_request: str):
        return [
            {"id": str(uuid.uuid4())[:8], "description": f"Analyze: {user_request}", "role": "Architect", "dependencies": []},
            {"id": str(uuid.uuid4())[:8], "description": "Execute Implementation", "role": "Coder", "dependencies": []},
            {"id": str(uuid.uuid4())[:8], "description": "Verify Results", "role": "Reviewer", "dependencies": []}
        ]

# Singleton
commander = Commander()
