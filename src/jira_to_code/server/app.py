# src/jira_to_code/server/app.py

from openenv.core.env_server import create_web_interface_app
from src.jira_to_code.server.env import JiraToCodeEnv
from src.jira_to_code.models import JiraCodeAction, JiraCodeObservation
from fastapi import FastAPI
import uvicorn
import os

# ✅ Instantiate env (important)
env = JiraToCodeEnv()

# Create base app
app = create_web_interface_app(env, JiraCodeAction, JiraCodeObservation)

# ✅ Add root route AFTER app creation
@app.get("/")
def root():
    return {"message": "Jira-to-Code running"}

# Optional health check (good practice)
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Ensure HF runs correctly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("src.jira_to_code.server.app:app", host="0.0.0.0", port=port)