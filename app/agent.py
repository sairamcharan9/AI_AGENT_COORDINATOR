# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LinkedIn Post Creator - Multi-agent system with iterative refinement workflow."""

import os
import platform
import requests
import logging
from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import load_artifacts, load_memory, get_user_choice, transfer_to_agent
from google.adk.tools import google_search
from google.adk.tools.load_web_page import load_web_page
from google.adk.code_executors import VertexAiCodeExecutor

from dotenv import load_dotenv
from . import prompt

# Import sub-agents from their respective modules
from .SUB_AGENTS.LinkedIN_Agent.agent import linkedin_writer_agent
from .SUB_AGENTS.Resume_Agent.agent import resume_writer_agent
from .SUB_AGENTS.PythonAgent.agent import python_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get model from environment
MODEL = os.getenv("LINKEDIN_MODEL", "gemini-2.5-pro-preview-05-06")


google_search_agent = LlmAgent(
    name="my_coordinator",
    model=MODEL,
    description=(
        "You Help with Google Search"
    ),
    instruction="""You help with google search give descriptive results ,upto date relavent information, include one or two urls to websites""",  # Using existing coordinator prompt
    tools=[google_search]
)



async def call_google_tool(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Direct wrapper for the Google search tool.
    
    Args:
        query: The search query
        tool_context: The tool context containing state
        
    Returns:
        The search results in a structured format
    """

    google_search_agent_tool = AgentTool(agent=google_search_agent)
    # Use the built-in Google search tool directly
    results = await google_search_agent_tool.run_async(
        args={"request": query}, tool_context=tool_context
    )

    if "google_search_output" in tool_context.state:
        # Store previous results in history
        tool_context.state["google_search_output"] = {
            "search_history": tool_context.state["google_search_output"],
            "latest_search": results
        }
    else:
        # First search, just store results directly
        tool_context.state["google_search_output"] = results
        
    return results
# Create Agent Tools for the coordinator
linkedin_writer_agent_tool = AgentTool(agent=linkedin_writer_agent)
resume_writer_agent_tool = AgentTool(agent=resume_writer_agent)
python_agent_tool = AgentTool(agent=python_agent)


# Coordinator agent that allows flexible usage of components
my_coordinator = LlmAgent(
    name="my_coordinator",
    model=MODEL,
    description=(
        "A versatile content creation and data analysis assistant that helps with "
        "LinkedIn posts, resume writing, web searches, and Python programming tasks."
    ),
    instruction=prompt.MY_COORDINATOR_PROMPT,  # Using existing coordinator prompt
    tools=[
        call_google_tool,
        linkedin_writer_agent_tool,
        resume_writer_agent_tool,
        python_agent_tool,
        load_artifacts,
        load_memory,
        get_user_choice,
        transfer_to_agent
    ]
)

# Set the root agent to be the coordinator for maximum flexibility
root_agent = my_coordinator