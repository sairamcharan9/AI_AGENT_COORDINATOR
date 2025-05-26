"""Python Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.adk.code_executors import VertexAiCodeExecutor
from typing import Dict, Any

from .prompt import PYTHON_AGENT_PROMPT

# Get model from environment
MODEL = os.getenv("LINKEDIN_MODEL", "gemini-2.5-pro-preview-05-06")

# Python Agent for code generation and data analysis
python_agent = LlmAgent(
    model=MODEL,
    name="Python_agent",
    instruction=PYTHON_AGENT_PROMPT,
    description="Python code assistant for data analysis and programming tasks",
    output_key="python_output",
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)
