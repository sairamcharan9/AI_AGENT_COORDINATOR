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

"""Tools for the Multi-Agent System."""

from typing import Dict, Any
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import google_search

async def call_google_agent(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Direct wrapper for the Google search tool.
    
    Args:
        query: The search query
        tool_context: The tool context containing state
        
    Returns:
        The search results in a structured format
    """
    # Use the built-in Google search tool directly
    results = await google_search(query=query, tool_context=tool_context)

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