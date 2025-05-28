"""File Handler Agent implementation."""

import os
from google.adk.agents import LlmAgent
from typing import Dict, Any

from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from .prompt import FILE_HANDLER_AGENT_PROMPT
from .tools import *

# Get model from environment
# File Handler agent specific model
FILE_HANDLER_MODEL = os.getenv("FILE_HANDLER_MODEL", os.getenv("MODEL", "gemini-2.5-flash-preview-05-20"))

# Get the project data directory from environment variables
PROJECT_DATA_DIRECTORY = os.getenv("PROJECT_DATA_DIRECTORY", "/")

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with file handling capabilities."""
    # Initialize any necessary state
    callback_context.state["file_handler_initialized"] = True
    callback_context.state["project_data_directory"] = PROJECT_DATA_DIRECTORY


file_handler_agent = LlmAgent(
    name="FileHandler",
    model=FILE_HANDLER_MODEL,
    instruction=FILE_HANDLER_AGENT_PROMPT, 
    tools = [
        read_file,
        write_to_file,
        create_new_file,
        create_new_folder,
        delete_file,
        delete_folder,
        list_files_with_metadata,
        check_file_exists,
        append_to_file,
        rename_file,
        copy_file,
        check_is_directory,
        check_is_file,
        search_file_content,
        set_working_directory,
        get_current_working_directory,
        list_folder_tree,
        get_file_permissions,
        set_file_permissions,
        get_file_metadata,
        compare_files,
        calculate_file_hash,
        zip_files,
        extract_zip,
        batch_process_files,
        filter_file_content,
    ],
    description="Manages file system operations safely and efficiently.",
    before_agent_callback=setup_before_agent_call,
    output_key="file_handler_output"
)