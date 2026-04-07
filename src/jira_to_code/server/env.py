# src/jira_to_code/server/env.py
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any

from openenv.core.env_server import Environment, State
from src.jira_to_code.models import JiraCodeAction, JiraCodeObservation

class JiraToCodeEnv(Environment):
    TASKS = {
        "easy": {
            "dir": "src/jira_to_code/tasks/easy",
            "ticket": "TICKET-101: Fix the off-by-one bug in calculator.add() function. It should correctly sum two numbers."
        },
        "medium": {
            "dir": "src/jira_to_code/tasks/medium",
            "ticket": "TICKET-201: Implement format_user_data in formatter.py. It should format dictionary data to 'LAST_NAME, First_name (Age: X)'. Handle missing age by defaulting to 'Unknown'."
        },
        "hard": {
            "dir": "src/jira_to_code/tasks/hard",
            "ticket": "TICKET-301: Implement an LRUCache class in lru_cache.py with put() and get() methods. O(1) time complexity expected. Evict least recently used when capacity is reached."
        }
    }

    def __init__(self):
        super().__init__()
        self.step_count = 0
        self.workspace_dir = None
        
        # Determine which task to run based on environment variable (defaults to easy)
        self.task_level = os.getenv("JIRA_TASK_LEVEL", "easy").lower()
        if self.task_level not in self.TASKS:
            self.task_level = "easy"
            
        self.task_source_dir = Path(self.TASKS[self.task_level]["dir"]).resolve()
        self.jira_ticket = self.TASKS[self.task_level]["ticket"]

    def _get_file_tree(self) -> list[str]:
        if not self.workspace_dir:
            return []
        tree = []
        for root, _, files in os.walk(self.workspace_dir):
            for file in files:
                if "__pycache__" in root or file.endswith(".pyc"):
                    continue
                rel_path = Path(root) / file
                tree.append(str(rel_path.relative_to(self.workspace_dir)))
        return tree

    async def reset(self) -> JiraCodeObservation:
        self.step_count = 0
        if self.workspace_dir and Path(self.workspace_dir).exists():
            shutil.rmtree(self.workspace_dir)
            
        self.workspace_dir = tempfile.mkdtemp(prefix=f"jira_env_{self.task_level}_")
        
        if self.task_source_dir.exists():
            shutil.copytree(self.task_source_dir, self.workspace_dir, dirs_exist_ok=True)
        else:
            print(f"Warning: Task directory {self.task_source_dir} not found!")
            
        return JiraCodeObservation(
            jira_ticket=self.jira_ticket,
            file_tree=self._get_file_tree()
        )

    async def step(self, action: JiraCodeAction) -> Tuple[JiraCodeObservation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        reward = 0.0
        done = False
        current_file_content = None
        test_output = None
        error = None

        workspace_path = Path(self.workspace_dir).resolve()

        try:
            if action.action_type in ["read_file", "write_file"]:
                if not action.file_path:
                    error = "file_path must be provided for read/write actions."
                else:
                    target_path = (workspace_path / action.file_path).resolve()
                    if not target_path.is_relative_to(workspace_path):
                        error = "Access denied: cannot access files outside workspace."
                    elif action.action_type == "read_file":
                        if target_path.exists():
                            current_file_content = target_path.read_text()
                        else:
                            error = f"File not found: {action.file_path}"
                    elif action.action_type == "write_file":
                        if action.content is None:
                            error = "content must be provided for write_file action."
                        else:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            target_path.write_text(action.content)
                            current_file_content = action.content

            elif action.action_type == "run_tests":
                result = subprocess.run(["pytest"], cwd=self.workspace_dir, capture_output=True, text=True)
                test_output = result.stdout + "\n" + result.stderr
                if result.returncode == 0:
                    reward = 0.5 
                elif result.returncode == 1:
                    reward = 0.1  
                else:
                    reward = -0.1 

            elif action.action_type == "submit":
                result = subprocess.run(["pytest"], cwd=self.workspace_dir, capture_output=True, text=True)
                test_output = result.stdout + "\n" + result.stderr
                done = True
                if result.returncode == 0:
                    reward = 1.0  
                else:
                    reward = 0.0  

        except Exception as e:
            error = f"System error: {str(e)}"
            reward = -0.2 

        obs = JiraCodeObservation(
            jira_ticket=self.jira_ticket,
            file_tree=self._get_file_tree(),
            current_file_content=current_file_content,
            test_output=test_output,
            error=error
        )
        return obs, reward, done, {}

    async def state(self) -> State:
        return State(episode_id=f"jira-{self.task_level}-{self.step_count}", step_count=self.step_count)
    
    async def close(self):
        if self.workspace_dir and Path(self.workspace_dir).exists():
            shutil.rmtree(self.workspace_dir)