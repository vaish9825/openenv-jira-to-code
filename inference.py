# inference.py
import asyncio
import json
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
from dotenv import load_dotenv # <-- Add this

# Load environment variables from .env file
load_dotenv()

# Our environment directly for local testing
from src.jira_to_code.server.env import JiraToCodeEnv
from src.jira_to_code.models import JiraCodeAction

# Read from env (with fallbacks just in case)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3.5:2b")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")

TASK_NAME = "easy-bug-fix"
BENCHMARK = "jira-to-code"
MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 1.0

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert software engineer resolving Jira tickets.
    You will receive the objective, the current file tree, and output from actions.
    
    You MUST respond with ONLY a valid JSON object representing your next action. 
    Do not include markdown blocks, explanations, or any other text.
    
    Valid action_types: "read_file", "write_file", "run_tests", "submit"
    
    JSON Schema:
    {
      "action_type": "string",
      "file_path": "string or null",
      "content": "string or null"
    }
    
    Example 1: {"action_type": "read_file", "file_path": "calculator.py", "content": null}
    Example 2: {"action_type": "write_file", "file_path": "calculator.py", "content": "def add(a, b):\n    return a + b"}
    Example 3: {"action_type": "run_tests", "file_path": null, "content": null}
    Example 4: {"action_type": "submit", "file_path": null, "content": null}
    """
).strip()

# --- MANDATORY LOGGING FUNCTIONS ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# --- AGENT LOGIC ---
def build_user_prompt(step: int, obs, last_reward: float) -> str:
    return textwrap.dedent(
        f"""
        Step: {step}
        Ticket: {obs.jira_ticket}
        File Tree: {obs.file_tree}
        Last Read/Write Content: {obs.current_file_content or 'None'}
        Test Output: {obs.test_output or 'None'}
        Error: {obs.error or 'None'}
        Last Reward: {last_reward}
        
        Determine your next action and return ONLY the JSON.
        """
    ).strip()

def get_action_from_llm(client: OpenAI, step: int, obs, last_reward: float) -> JiraCodeAction:
    user_prompt = build_user_prompt(step, obs, last_reward)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1, # Keep it low for coding/JSON accuracy
            max_tokens=500,
        )
        raw_text = (completion.choices[0].message.content or "").strip()
        
        # Clean up in case the model wraps JSON in markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).replace("```", "", 1).strip()
            
        action_dict = json.loads(raw_text)
        return JiraCodeAction(**action_dict), raw_text
        
    except Exception as exc:
        # Fallback action if parsing fails so the environment doesn't crash
        error_msg = f"LLM Parsing Error: {exc}"
        return JiraCodeAction(action_type="read_file", file_path="calculator.py"), error_msg

# --- MAIN LOOP ---
async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = JiraToCodeEnv()

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = await env.reset()
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            action, raw_action_str = get_action_from_llm(client, step, obs, last_reward)
            
            # Escape newlines for single-line logging
            safe_action_str = raw_action_str.replace('\n', '\\n').replace('\r', '')

            # Take step in environment
            obs, reward, done, _ = await env.step(action)
            error = obs.error

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step=step, action=safe_action_str, reward=reward, done=done, error=error)

            if done:
                break

        # Calculate final score (clamp between 0 and 1)
        score = min(max(sum(rewards), 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        await env.close()
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())