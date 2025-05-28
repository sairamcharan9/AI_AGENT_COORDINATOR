"""LinkedIn Main Agent implementation.

This agent coordinates LinkedIn-related tasks by delegating to specialized sub-agents.
"""

import os
from google.adk.agents import SequentialAgent
from typing import Dict, Any

from .prompt import LINKEDIN_AGENT_PROMPT # Import the main agent's prompt

# Import sub-agents
from .SUB_AGENTS.LINKEDINWRITER.agent import linkedin_writer_agent
from .SUB_AGENTS.LINKEDINOPTIMIZER.agent import linkedin_optimizer_agent

# Get model from environment variables or use default
# LinkedIn agent specific model, falls back to main MODEL if not specified
LINKEDIN_MODEL = os.getenv("LINKEDIN_MODEL", os.getenv("MODEL", "gemini-2.5-flash-preview-05-20"))


linkedin_agent = SequentialAgent( # Changed Agent to LlmAgent
    name="LinkedInAgent",
    description="An agent that coordinates LinkedIn post creation and optimization tasks.", # Clarified description
    sub_agents=[linkedin_writer_agent,linkedin_optimizer_agent], # Removed AgentTool wrappers around sub-agents. Add other tools needed by this coordinating agent if any.
)
