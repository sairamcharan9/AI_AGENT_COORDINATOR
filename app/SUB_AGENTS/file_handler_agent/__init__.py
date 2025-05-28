"""File Handler Agent Module.

This module provides an LlmAgent specialized in managing file system operations safely and efficiently.
"""

from .agent import file_handler_agent
from .tools import *

__all__ = [
    "file_handler_agent",
    "read_file",
    "write_to_file",
    "create_new_file",
    "create_new_folder",
    "delete_file",
    "delete_folder",
    "list_files_with_metadata",
    "check_file_exists",
    "append_to_file",
    "rename_file",
    "copy_file",
    "check_is_directory",
    "check_is_file",
    "get_current_working_directory",
    "list_folder_tree",
    "get_file_permissions",
    "set_file_permissions",
    "filter_file_content",
    "get_file_metadata",
    "compare_files",
    "calculate_file_hash",
    "zip_files",
    "extract_zip",
    "batch_process_files",
    "search_file_content",
    "set_working_directory"
]
