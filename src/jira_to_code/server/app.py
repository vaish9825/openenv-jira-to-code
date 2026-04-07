# src/jira_to_code/server/app.py
from openenv.core.env_server import create_web_interface_app
from src.jira_to_code.server.env import JiraToCodeEnv
from src.jira_to_code.models import JiraCodeAction, JiraCodeObservation

# Initialize the environment
env = JiraToCodeEnv

# Create the FastAPI app with the OpenEnv wrapper
app = create_web_interface_app(env, JiraCodeAction, JiraCodeObservation)

def serve():
    """Entry point for the OpenEnv validator to run the server."""
    uvicorn.run("src.jira_to_code.server.app:app", host="0.0.0.0", port=8000)