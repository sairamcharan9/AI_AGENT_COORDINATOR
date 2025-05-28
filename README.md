# My Awesome Agent

Welcome to My Awesome Agent! This project leverages advanced AI models to create a versatile and intelligent agent capable of performing various tasks, from generating LinkedIn posts and resumes to handling file system operations and providing Python programming assistance.

---

## 🚀 Setup & Installation

Follow these steps to get My Awesome Agent up and running on your local machine.

### Prerequisites

*   **Python 3.11+**: Ensure you have Python 3.11 or a newer version installed.
*   **Poetry**: We use Poetry for dependency management. If you don't have it, install it via `pip`:
    ```bash
    pip install poetry
    ```
*   **UV (Optional but Recommended)**: For faster dependency resolution and installation, install UV:
    ```bash
    pip install uv
    ```

### Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/my-awesome-agent.git
    cd my-awesome-agent
    ```

2.  **Install Dependencies**:
    Using UV (recommended for speed):
    ```bash
    uv pip install "poetry==1.8.2" # Install poetry with uv
    uv venv # Create virtual environment with uv
    uv pip install -e ".[dev]" # Install project dependencies including dev dependencies
    ```
    Alternatively, using Poetry (if UV is not used or preferred):
    ```bash
    poetry install --with dev
    ```

3.  **Set Up Environment Variables**:
    Create a `.env` file in the root directory of the project based on `.env-example`. This file will store your API keys and other configurations.
    ```bash
    cp .env-example .env
    ```
    Open `.env` and fill in the necessary values. **Do NOT commit your `.env` file to version control!**

4.  **Activate Virtual Environment**:
    If you're using Poetry:
    ```bash
    poetry shell
    ```
    If you're using UV with `uv venv` (and added it to your PATH):
    ```bash
    source .venv/bin/activate # On macOS/Linux
    .venv\Scripts\activate   # On Windows
    ```

---

## 🛠️ Development

### Local Setup

*   **Pre-commit Hooks**: We use pre-commit hooks to ensure code quality and consistency. Install them after setting up your environment:
    ```bash
    pre-commit install
    ```
    This will run checks like linting and formatting before each commit.

### Running the Agent

Instructions on how to run the agent locally for development and testing will go here. (e.g., `python -m app.main` or specific API endpoint calls).

### Testing

Details on how to run tests and the testing framework used will be provided here. (e.g., `pytest`).

---

## 📂 Project Structure

```
.
├── .github/                       # GitHub Actions workflows
├── .pre-commit-config.yaml        # Pre-commit hook configurations
├── .vscode/                       # VS Code editor settings
├── app/                           # Main application source code
│   ├── SUB_AGENTS/                # Individual AI agents
│   │   ├── file_handler_agent/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   │   ├── tools.py
│   │   │   └── __init__.py
│   │   ├── LinkedIN_Agent/
│   │   │   ├── SUB_AGENTS
│   │   │   │   ├── LINKEDINOPTIMIZER
│   │   │   │   │   ├── agent.py
│   │   │   │   │   ├── prompt.py
│   │   │   │   │   └── __init__.py
│   │   │   │   └── LINKEDINWRITER
│   │   │   │       ├── agent.py
│   │   │   │       ├── prompt.py
│   │   │   │       └── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   │   └── __init__.py
│   │   ├── PythonAgent/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   │   └── __init__.py
│   │   └── Resume_Agent/
│   │       ├── agent.py
│   │       ├── prompt.py
│   │       └── __init__.py
│   ├── utils/                     # Utility functions and data
│   │   ├── data
│   │   │   ├── logos
│   │   │   │   ├── InnovateAI_logo.jpg
│   │   │   │   └── logo.jpg
│   │   │   ├── data-science-architecture.png
│   │   │   ├── evalset5eb406.evalset.json
│   │   │   ├── praveen.tex
│   │   │   ├── README.md
│   │   │   └── retail_demand_data.csv
│   │   ├── rag.py
│   │   ├── utils.py
│   │   └── utils.py.original
│   ├── agent.py                   # Coordinator agent logic
│   ├── callbacks.py               # Callback functions for agent execution
│   ├── coordinator_prompt.py      # Prompt for the coordinator agent
│   ├── prompt.py                  # General prompt templates
│   └── tools.py                   # Definitions of tools available to the agent
├── deployment/                    # Deployment configurations (e.g., Dockerfiles)
├── eval/                          # Evaluation scripts and datasets
├── notebooks/                     # Jupyter notebooks for experimentation
├── tests/                         # Unit and integration tests
├── .env-example                   # Example environment variables file
├── Dockerfile                     # Docker build instructions
├── Makefile                       # Makefile for common development tasks
├── MODEL_CONFIG.md                # Model configuration details
├── pyproject.toml                 # Poetry project configuration
├── README.md                      # Project overview and documentation
└── poetry.lock                    # Poetry lock file for reproducible builds
```

---

## 🤖 Agents & Capabilities

My Awesome Agent is composed of several specialized sub-agents, each designed to handle specific tasks:

### 🧠 Coordinator Agent

*   **Role**: The central intelligence that understands user requests, determines the most suitable sub-agent or tool to use, and orchestrates the workflow.
*   **Capabilities**:
    *   **Tool Coordination**: Directs specific tasks to the most appropriate specialized agent (e.g., LinkedIn Writer, Resume Writer).
    *   **Web Search & Analysis**: Coordinates web searches and web page analyses using the Google Search tool.
    *   **User Interaction**: Presents search results and web content in a clear, organized format.
    *   **Decision Making**: Facilitates user choices for important decisions by presenting options.
    *   **Memory & Context**: Accesses past conversations, preferences, or knowledge to provide contextual assistance.

### ✍️ LinkedIn Writer Agent

*   **Role**: Creates engaging and professional LinkedIn posts.
*   **Capabilities**:
    *   **Content Generation**: Generates complete LinkedIn posts based on user-provided topics and style preferences.
    *   **Image Prompts**: Provides complementary image prompts to enhance post engagement.
    *   **Professional Formatting**: Ensures posts adhere to professional LinkedIn standards.

### 📄 Resume Writer Agent

*   **Role**: Generates and optimizes professional resumes tailored for specific job applications.
*   **Capabilities**:
    *   **Tailored Resumes**: Creates resumes customized for specific job targets, experience levels, and key skills.
    *   **ATS Optimization**: Designs resumes to be Applicant Tracking System (ATS) friendly, maximizing visibility to recruiters.
    *   **Content Customization**: Integrates professional background details and skills effectively.

### 🎨 Logo Create Agent (Image Generation)

*   **Role**: Creates high-quality, professional logos and images for business use.
*   **Capabilities**:
    *   **Design Generation**: Generates logos and images based on brand requirements, style preferences, and image purpose.
    *   **Design Explanation**: Provides explanations for the design choices made.

### 💻 Python Agent

*   **Role**: Assists with Python programming tasks and data analysis.
*   **Capabilities**:
    *   **Code Generation**: Writes Python code snippets based on descriptions.
    *   **Data Analysis**: Performs data analysis tasks and provides results or explanations.
    *   **Code Explanation**: Explains complex Python code or technical concepts.

### 🗃️ File Handler Agent

*   **Role**: Manages all file system operations safely and efficiently.
*   **Capabilities**:
    *   **Read/Write Files**: Reads and writes content to files.
    *   **Create/Delete**: Creates new files and directories, and safely deletes existing ones (with user confirmation).
    *   **List/Explore**: Lists directory contents (with metadata) and explores directory structures.
    *   **Permissions**: Manages file permissions.
    *   **Rename/Copy**: Renames and copies files and directories.
    *   **Safety**: Implements checks (e.g., confirm before overwrite/delete) to prevent data loss.

### 🌐 Google Search Tool

*   **Role**: Performs web searches to find relevant information.
*   **Capabilities**:
    *   **Information Retrieval**: Executes search queries on Google.
    *   **Result Presentation**: Provides search results with titles, snippets, and links.

---

## 🔧 Tooling

*   **Poetry**: Dependency management.
*   **UV**: Faster dependency resolution.
*   **Pre-commit**: Code quality hooks.
*   **Pytest**: Testing framework.
*   **Black, isort, flake8**: Code formatting and linting.
*   **Docker**: Containerization.

---

## 📈 Roadmap

*   **Phase 1: Core Agent Development** (Current)
    *   Implement and refine Coordinator Agent logic.
    *   Develop and integrate LinkedIn Writer, Resume Writer, Python Agent, and File Handler.
    *   Establish robust testing and evaluation frameworks.
*   **Phase 2: Enhanced Capabilities**
    *   Integrate Logo Create Agent.
    *   Add more advanced data analysis capabilities to Python Agent.
    *   Improve contextual understanding and memory management for the Coordinator.
*   **Phase 3: Deployment & Scaling**
    *   Set up CI/CD pipelines.
    *   Optimize for cloud deployment.
    *   Explore advanced user interfaces.
*   **Phase 4: New Agent Development**
    *   Introduce new specialized agents based on user needs (e.g., Email Composer, Research Assistant).

---

## 🤝 Contributing

We welcome contributions! Please see our `CONTRIBUTING.md` (to be created) for guidelines.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 📧 Contact

For questions or support, please open an issue on GitHub or contact [Your Email Address].