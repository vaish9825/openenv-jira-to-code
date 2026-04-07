# src/jira_to_code/server/env.py
from typing import Tuple, Dict, Any
from openenv.core.env_server import Environment, State
from src.jira_to_code.models import JiraCodeAction, JiraCodeObservation

class JiraToCodeEnv(Environment):
    def __init__(self):
        super().__init__()
        self.current_task = None
        self.workspace_dir = None
        self.step_count = 0
        
    async def reset(self) -> JiraCodeObservation:
        """Initialize a new episode, return initial observation."""
        self.step_count = 0
        return JiraCodeObservation(
            jira_ticket="TICKET-123: Fix off-by-one error in calculator.py",
            file_tree=["calculator.py", "tests/test_calculator.py"],
            current_file_content=None,
            test_output=None,
            error=None
        )

    async def step(self, action: JiraCodeAction) -> Tuple[JiraCodeObservation, float, bool, Dict[str, Any]]:
        """Execute action, return resulting Observation, reward, done, info."""
        self.step_count += 1
        
        obs = JiraCodeObservation(
            jira_ticket="TICKET-123: Fix off-by-one error in calculator.py",
            file_tree=["calculator.py", "tests/test_calculator.py"],
            current_file_content="def add(a, b):\n    return a + b + 1  # BUG",
            test_output=None,
            error=None
        )
        
        # Standard format: observation, reward, done, info dict
        return obs, 0.0, False, {}

    async def state(self) -> State:
        """Access episode metadata."""
        return State(episode_id="test-123", step_count=self.step_count)