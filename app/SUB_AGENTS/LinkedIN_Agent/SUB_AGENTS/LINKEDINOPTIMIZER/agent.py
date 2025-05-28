"""LinkedIn Optimizer Agent implementation."""
import os
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from typing import Dict, Any
from .prompt import LINKEDIN_OPTIMIZER_PROMPT # Changed prompt

# Get model from environment variables or use default
MODEL = os.getenv("LINKEDIN_MODEL", "gemini-2.5-pro-preview-05-06")

# LinkedIn Optimizer Agent (Optimizes LinkedIn profiles and content)
linkedin_optimizer_agent = LlmAgent( # Changed variable name
    name="LinkedInOptimizer", # Changed name
    model=MODEL,
    instruction=LINKEDIN_OPTIMIZER_PROMPT, # Changed prompt usage
    tools=[google_search],  # Use google search tool
    description="Optimizes LinkedIn profiles and content for better visibility and engagement.", # Changed description
    output_key="optimizer_output" # Changed output key
)
