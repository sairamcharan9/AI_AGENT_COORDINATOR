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

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""
import os
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from .sub_agents import bqml_agent
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from .prompts import return_instructions_root
from .tools import call_db_agent, call_ds_agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters



date_today = date.today()
# date_today = date.today() # Remove from global scope, will be handled in callback


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""
    current_date = date.today() # Get current date inside the callback

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    # The agent's base instruction is set during Agent initialization.
    # We will prepend the date and append the schema to it.
    current_agent_instruction = callback_context._invocation_context.agent.instruction
    if not current_agent_instruction: # Should be set from Agent constructor
        current_agent_instruction = return_instructions_root()

    # Prepend date
    dated_instruction = (
        f"Today's date is: {current_date}.\n\n"
        f"{current_agent_instruction}"
    )

    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]
        final_instruction = (
            dated_instruction
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )
        callback_context._invocation_context.agent.instruction = final_instruction
    else:
        callback_context._invocation_context.agent.instruction = dated_instruction



TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/")


data_science_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-flash-latest"),
    name="db_ds_multiagent",
    instruction=return_instructions_root(), # Initial instruction
    global_instruction=( # Static global instruction
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        """
    ),
    sub_agents=[bqml_agent],
    tools=[
        call_db_agent,
        call_ds_agent,
        load_artifacts,
        
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
