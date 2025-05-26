"""LinkedIn Writer Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from typing import Dict, Any
from .prompt import LINKEDIN_WRITER_PROMPT

# Get model from environment variables or use default
MODEL = os.getenv("LINKEDIN_MODEL", "gemini-2.5-pro-preview-05-06")

# LinkedIn Writer Agent (Creates LinkedIn posts and image prompts)
linkedin_writer_agent = LlmAgent(
    name="LinkedInWriter",
    model=MODEL,
    instruction=LINKEDIN_WRITER_PROMPT,
    tools=[google_search],  # Use google search tool
    description="Creates LinkedIn posts with formatted content and complementary image prompts in JSON format.",
    output_key="writer_output"
)