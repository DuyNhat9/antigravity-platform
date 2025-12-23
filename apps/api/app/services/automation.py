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
        delay 1.0
        tell application "System Events"
            tell process "{self.app_name}"
                -- 1. Press Escape multiple times to exit any open menus or focus in editor
                key code 53 
                delay 0.2
                key code 53
                delay 0.5
                
                -- 2. Open/Focus Chat (Cmd+L)
                keystroke "l" using {{command down}}
                delay 1.0
                
                -- 3. Clear existing text in chat box (Cmd+A -> Backspace)
                keystroke "a" using {{command down}}
                delay 0.2
                key code 51
                delay 0.3
                
                -- 4. Type the mission mandate
                keystroke "{prompt}"
                delay 0.5
                
                -- 5. Final Enter to send
                key code 36
            end tell
        end tell
        '''
        
        result = run_applescript(script)
        if result is not None:
             await blackboard.add_log("System", f"UI Trigger sent to {self.app_name}.")
        else:
             await blackboard.add_log("System", "Failed to send UI trigger. Check Accessibility permissions.")

# Singleton
automation = AutomationService(app_name=os.getenv("IDE_APP_NAME", "Antigravity"))
