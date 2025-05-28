"""Python Agent implementation."""

import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import VertexAiCodeExecutor
from typing import Dict, Any

from .prompt import PYTHON_AGENT_PROMPT
# Import the File Handler Agent
from ..file_handler_agent import file_handler_agent

# Get model from environment
# Python agent specific model, falls back to main MODEL if not specified
PYTHON_MODEL = os.getenv("PYTHON_MODEL", os.getenv("MODEL", "gemini-2.5-flash-preview-05-20"))

# Create an AgentTool for the File Handler Agent
file_handler_agent_tool = AgentTool(agent=file_handler_agent)

# Python Agent for code generation and data analysis
python_agent = Agent(
    model=PYTHON_MODEL,
    name="Python_agent",
    instruction=PYTHON_AGENT_PROMPT,
    description="Python code assistant for data analysis and programming tasks",
    output_key="python_output",
    tools=[
        file_handler_agent_tool,  # Add File Handler Agent as a tool
    ],
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)
