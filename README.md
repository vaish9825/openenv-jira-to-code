---
title: Jira-To-Code Agent Environment
emoji: 🛠️
colorFrom: indigo
colorTo: slate
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🚀 Jira-To-Code: The Ultimate RL Coding Environment

[![OpenEnv Validated](https://img.shields.io/badge/OpenEnv-Validated-green.svg)](https://github.com/meta-pytorch/OpenEnv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Jira-To-Code** is a high-fidelity Reinforcement Learning (RL) environment designed for the **Meta/Hugging Face OpenEnv Hackathon**. It challenges AI agents to act as Senior Software Engineers by resolving real-world Jira tickets within a secure, sandboxed codebase.

---

## 🌟 Key Features

*   **⚡ ReAct Ready**: Built-in support for Thought-Action-Observation loops.
*   **🧠 Episodic Memory**: Maintains full conversational history for multi-turn reasoning.
*   **📊 6 Diverse Tasks**: From simple bug fixes to complex data structure implementations.
*   **📈 Rich Reward Shaping**: Partial credit for passing tests, step penalties for efficiency, and shaping rewards for active coding.
*   **🛡️ Robust Parsing**: Resilient JSON extraction and self-correction prompt injection.

---

## 🏗️ Environment Architecture

Agents interact with the environment via a standardized FastAPI interface:

| Action | Description |
| :--- | :--- |
| `list_files` | Explore the workspace directory structure. |
| `read_file` | Read the content of a specific file. |
| `write_file` | Create or overwrite code in the workspace. |
| `run_tests` | Execute `pytest` and receive detailed traceback output. |
| `submit` | Finalize the task and receive the definitive score. |

---

## 🎯 Task Tiers

1.  **Easy**: Bug fixes (Calculator off-by-one, String vowel counting).
2.  **Medium**: Implementation from specs (User data formatter, Email/Password validator).
3.  **Hard**: Complex logic (LRU Cache O(1), Directed Graph & Topological Sort).

---

## 🚀 Getting Started

### 1. Local Setup
```bash
# Clone the repository
git clone https://huggingface.co/spaces/Navigam/jira-to-code
cd jira-to-code

# Create and activate environment
uv venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install -e .
```

### 2. Run Inference
```bash
# Run the full baseline agent against all tasks
uv run python inference.py

# Run a specific task
uv run python inference.py --tasks easy_2,medium
```

### 3. Docker Deployment
```bash
docker build -t jira-to-code .
docker run -p 7860:7860 jira-to-code
```

---

## 🏆 Scoring Rubric Alignment

This environment is optimized for high marks in the OpenEnv Hackathon:
*   **Real-world Utility**: Models a developer's daily workflow.
*   **Task/Grader Quality**: Deterministic `pytest` grading with partial credit.
*   **Environment Design**: Gymnasium-style API with comprehensive observation space.
*   **Code Quality**: Passes `openenv validate` and follows strict Pydantic typing.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ for the OpenEnv Hackathon by <a href="https://huggingface.co/Navigam">Navigam</a></sub>
</div>
