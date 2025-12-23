import subprocess
import os
from .blackboard import blackboard

def run_applescript(script: str):
    """Executes an AppleScript and returns the output."""
    try:
        process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if stderr:
             print(f"AppleScript Error: {stderr}")
        return stdout.strip()
    except Exception as e:
        print(f"Failed to run AppleScript: {e}")
        return None

class AutomationService:
    def __init__(self, app_name: str = "Antigravity"):
        self.app_name = app_name

    async def trigger_agent(self, role: str, description: str):
        """
        Activates the IDE, opens chat, and injects the mission prompt.
        """
        await blackboard.add_log("System", f"Triggering {role} via UI Automation...")
        
        prompt = f"Agent {role}, your mission is: {description}. Please execute and report back through the MCP tool."
        
        # AppleScript to: 
        # 1. Activate App
        # 2. Command+L (Open Chat/Sidebar)
        # 3. Type text
        # 4. Press Enter
        script = f'''
        tell application "{self.app_name}" to activate
        delay 0.5
        tell application "System Events"
            -- Open Chat (Cmd+L is typical for Cursor and Antigravity)
            keystroke "l" using {{command down}}
            delay 0.5
            -- Type the mandate
            keystroke "{prompt}"
            delay 0.2
            -- Enter to send
            key code 36
        end tell
        '''
        
        result = run_applescript(script)
        if result is not None:
             await blackboard.add_log("System", f"UI Trigger sent to {self.app_name}.")
        else:
             await blackboard.add_log("System", "Failed to send UI trigger. Check Accessibility permissions.")

# Singleton
automation = AutomationService(app_name=os.getenv("IDE_APP_NAME", "Antigravity"))
