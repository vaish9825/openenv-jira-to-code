from src.jira_to_code.server.app import app

import uvicorn


def main() -> None:
    """Production server entrypoint expected by OpenEnv validate."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
