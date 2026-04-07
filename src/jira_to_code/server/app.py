# src/jira_to_code/server/app.py
import os
import uvicorn
from fastapi import FastAPI
from openenv.core.env_server import create_web_interface_app
from src.jira_to_code.server.env import JiraToCodeEnv
from src.jira_to_code.models import JiraCodeAction, JiraCodeObservation

env = JiraToCodeEnv

app = create_web_interface_app(env, JiraCodeAction, JiraCodeObservation)

@app.get("/")
def root():
    return {"message": "Jira-to-Code running"}

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    port = int(os.environ.get("PORT", 7860))
    # Note the updated module path here!
    uvicorn.run("src.jira_to_code.server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()