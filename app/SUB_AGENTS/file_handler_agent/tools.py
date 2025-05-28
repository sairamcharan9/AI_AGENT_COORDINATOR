import os
import json
import logging
import shutil
import datetime
import re
import time
import hashlib
import zipfile
import filecmp
import stat
import platform
from io import BytesIO
from datetime import datetime

# Platform-specific imports
if platform.system() != "Windows":
    import pwd
    import grp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import psutil
from typing import List, Union, Dict, Any, Optional, Tuple, Callable, Set
from dotenv import load_dotenv
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Load environment variables
load_dotenv()

# Get the project data directory from environment variable
PROJECT_DATA_DIRECTORY = os.getenv("PROJECT_DATA_DIRECTORY", "/")

def read_file(file_path: str, use_data_dir: bool = True) -> str:
    """Reads the content of a file from either the project data directory or a full path.
    
    Args:
        file_path: Path to the file to read. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        The content of the file as a string. For JSON files, this will be the 
        JSON string representation.
    
    returns:
        FileNotFoundError: If the specified file cannot be found.
        Exception: For any other errors during file reading.
    """
    # Determine the full path based on the use_data_dir flag
    if use_data_dir:
        full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
    else:
        full_path = file_path
    
    # Check if the file exists
    if not os.path.isfile(full_path):
        logging.warning(f"File not found: {full_path}")
        return "file not found"    
    # Determine file type by extension
    _, file_extension = os.path.splitext(file_path)
    
    # Read and process the file based on its type
    if file_extension.lower() == '.json':
        with open(full_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert JSON to a string representation
            return json.dumps(data)
    else:
        # Default to text file reading (works for Python, text, and other files)
        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read()

def write_to_file(file_path: str, content: str, use_data_dir: bool = True) -> str:
    """Writes content to a file, creating it if it doesn't exist.
    
    Args:
        file_path: Path to the file to write. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        content: The string content to write to the file.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A success message with the path of the written file.
    
    returns:
        PermissionError: If there are permission issues when writing the file.
        Exception: For any other errors during file writing.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the content to the file
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully wrote to file: {full_path}"
    
    except PermissionError:
        error_msg = f"Permission denied when writing to file: {file_path}"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error writing to file {file_path}: {str(e)}"
        logging.error(error_msg)
        return error_msg


def create_new_file(file_path: str, content: str = "", use_data_dir: bool = True) -> str:
    """Creates a new file with optional initial content.
    
    Args:
        file_path: Path to the new file. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        content: Optional initial content for the file (default: empty string).
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A success message with the path of the created file.
    
    returns:
        FileExistsError: If the file already exists.
        PermissionError: If there are permission issues when creating the file.
        Exception: For any other errors during file creation.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file already exists
        if os.path.exists(full_path):
            error_msg = f"File already exists: {full_path}"
            logging.warning(error_msg)
            return error_msg
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Create the file with optional content
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully created new file: {full_path}"
    
    except FileExistsError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when creating file: {file_path}"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error creating file {file_path}: {str(e)}"
        logging.error(error_msg)
        return error_msg


def create_new_folder(folder_path: str, use_data_dir: bool = True) -> str:
    """Creates a new folder and any necessary parent directories.
    
    Args:
        folder_path: Path to the new folder. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/new_folder").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the folder_path.
            If False, use the folder_path as provided.
    
    Returns:
        A success message with the path of the created folder.
    
    returns:
        PermissionError: If there are permission issues when creating the folder.
        Exception: For any other errors during folder creation.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, folder_path)
        else:
            full_path = folder_path
        
        # Create the directory and any necessary parent directories
        os.makedirs(full_path, exist_ok=True)
        
        return f"Successfully created folder: {full_path}"
    
    except PermissionError:
        error_msg = f"Permission denied when creating folder: {folder_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error creating folder {folder_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(error_msg)


def delete_file(file_path: str, use_data_dir: bool = True) -> str:
    """Deletes a file.
    
    Args:
        file_path: Path to the file to delete. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A success message confirming the file deletion.
    
    returns:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are permission issues when deleting the file.
        Exception: For any other errors during file deletion.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            error_msg = f"File not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        # Delete the file
        os.remove(full_path)
        
        return f"Successfully deleted file: {full_path}"
    
    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when deleting file: {file_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error deleting file {file_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(error_msg)


def delete_folder(folder_path: str, use_data_dir: bool = True) -> str:
    """Deletes a folder and all its contents.
    
    Args:
        folder_path: Path to the folder to delete. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the folder_path.
            If False, use the folder_path as provided.
    
    Returns:
        A success message confirming the folder deletion.
    
    returns:
        FileNotFoundError: If the folder does not exist.
        PermissionError: If there are permission issues when deleting the folder.
        Exception: For any other errors during folder deletion.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, folder_path)
        else:
            full_path = folder_path
        
        # Check if the folder exists
        if not os.path.isdir(full_path):
            error_msg = f"Folder not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        # Delete the folder and all its contents
        shutil.rmtree(full_path)
        
        return f"Successfully deleted folder: {full_path}"
    
    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when deleting folder: {folder_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error deleting folder {folder_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)


def list_files_with_metadata(directory_path: str, use_data_dir: bool = True) -> List[dict]:
    """Lists all files and subdirectories in a directory, including their metadata.
    
    Args:
        directory_path: Path to the directory to list. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the directory_path.
            If False, use the directory_path as provided.
    
    Returns:
        A list of dictionaries, where each dictionary contains 'name', 'type',
        'size' (in bytes), 'creation_time', and 'modification_time' for each item.
    
    returns:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If there are permission issues when accessing the directory.
        Exception: For any other errors during directory listing or metadata retrieval.
    """
    try:
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_path = directory_path
        
        if not os.path.isdir(full_path):
            error_msg = f"Directory not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        items_with_metadata = []
        for item_name in os.listdir(full_path):
            item_full_path = os.path.join(full_path, item_name)
            try:
                stat_info = os.stat(item_full_path)
                item_type = "file" if os.path.isfile(item_full_path) else "directory"
                items_with_metadata.append({
                    "name": item_name,
                    "type": item_type,
                    "size": stat_info.st_size,
                    "creation_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    "modification_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                })
            except Exception as e:
                logging.warning(f"Could not retrieve metadata for {item_full_path}: {e}")
                items_with_metadata.append({
                    "name": item_name,
                    "type": "unknown",
                    "error": str(e)
                })
        
        return items_with_metadata
    
    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when listing directory: {directory_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error listing directory {directory_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def check_file_exists(file_path: str, use_data_dir: bool = True) -> bool:
    """Checks if a file exists.
    
    Args:
        file_path: Path to the file to check. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        True if the file exists, False otherwise.
    """
    if use_data_dir:
        full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
    else:
        full_path = file_path
    
    # Check if the file exists
    return os.path.isfile(full_path)


def append_to_file(file_path: str, content: str, use_data_dir: bool = True) -> str:
    """Appends content to an existing file.
    
    Args:
        file_path: Path to the file to append to. If use_data_dir is True, this should be a 
            relative path within the project data directory (e.g., "prompts/system.txt").
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        content: The string content to append to the file.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A success message with the path of the updated file.
    
    returns:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are permission issues when writing to the file.
        Exception: For any other errors during file writing.
    """
    try:
        # Determine the full path based on the use_data_dir flag
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            error_msg = f"File not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        # Append the content to the file
        with open(full_path, 'a', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully appended to file: {full_path}"
    
    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when appending to file: {file_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error appending to file {file_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(error_msg)


def rename_file(old_path: str, new_path: str, use_data_dir: bool = True) -> str:
    """Renames or moves a file.
    
    Args:
        old_path: Current path of the file. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        new_path: New path for the file. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        use_data_dir: If True (default), prepend the project data directory to both paths.
            If False, use the paths as provided.
    
    Returns:
        A success message with the old and new paths.
    
    returns:
        FileNotFoundError: If the source file does not exist.
        FileExistsError: If the destination file already exists.
        PermissionError: If there are permission issues.
        Exception: For any other errors during file renaming.
    """
    try:
        # Determine the full paths based on the use_data_dir flag
        if use_data_dir:
            full_old_path = os.path.join(PROJECT_DATA_DIRECTORY, old_path)
            full_new_path = os.path.join(PROJECT_DATA_DIRECTORY, new_path)
        else:
            full_old_path = old_path
            full_new_path = new_path
        
        # Check if the source file exists
        if not os.path.isfile(full_old_path):
            error_msg = f"Source file not found: {full_old_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        # Check if the destination file already exists
        if os.path.exists(full_new_path):
            error_msg = f"Destination file already exists: {full_new_path}"
            logging.warning(error_msg)
            return FileExistsError(error_msg)
        
        # Create directory for the new path if it doesn't exist
        os.makedirs(os.path.dirname(full_new_path), exist_ok=True)
        
        # Rename/move the file
        os.rename(full_old_path, full_new_path)
        
        return f"Successfully renamed/moved file from {full_old_path} to {full_new_path}"
    
    except FileNotFoundError as e:
        return e
    except FileExistsError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when renaming file from {old_path} to {new_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error renaming file from {old_path} to {new_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def copy_file(source_path: str, destination_path: str, use_data_dir: bool = True) -> str:
    """Copies a file from a source path to a destination path.
    
    Args:
        source_path: Path to the file to copy. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        destination_path: Path where the file should be copied to. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        use_data_dir: If True (default), prepend the project data directory to both paths.
            If False, use the paths as provided.
    
    Returns:
        A success message with the source and destination paths.
    
    returns:
        FileNotFoundError: If the source file does not exist.
        FileExistsError: If a file already exists at the destination path.
        PermissionError: If there are permission issues.
        Exception: For any other errors during file copying.
    """
    try:
        if use_data_dir:
            full_source_path = os.path.join(PROJECT_DATA_DIRECTORY, source_path)
            full_destination_path = os.path.join(PROJECT_DATA_DIRECTORY, destination_path)
        else:
            full_source_path = source_path
            full_destination_path = destination_path

        if not os.path.isfile(full_source_path):
            error_msg = f"Source file not found: {full_source_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)

        if os.path.exists(full_destination_path):
            error_msg = f"Destination file already exists: {full_destination_path}"
            logging.warning(error_msg)
            return FileExistsError(error_msg)
        
        os.makedirs(os.path.dirname(full_destination_path), exist_ok=True)
        
        shutil.copy2(full_source_path, full_destination_path)
        
        return f"Successfully copied file from {full_source_path} to {full_destination_path}"

    except FileNotFoundError as e:
        return e
    except FileExistsError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when copying file from {source_path} to {destination_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error copying file from {source_path} to {destination_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def check_is_directory(path: str, use_data_dir: bool = True) -> bool:
    """Checks if a given path is a directory.
    
    Args:
        path: Path to check. If use_data_dir is True, this should be a 
            relative path within the project data directory.
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the path.
            If False, use the path as provided.
    
    Returns:
        True if the path is a directory, False otherwise.
    """
    if use_data_dir:
        full_path = os.path.join(PROJECT_DATA_DIRECTORY, path)
    else:
        full_path = path
    
    return os.path.isdir(full_path)

def check_is_file(path: str, use_data_dir: bool = True) -> bool:
    """Checks if a given path is a file.
    
    Args:
        path: Path to check. If use_data_dir is True, this should be a 
            relative path within the project data directory.
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the path.
            If False, use the path as provided.
    
    Returns:
        True if the path is a file, False otherwise.
    """
    if use_data_dir:
        full_path = os.path.join(PROJECT_DATA_DIRECTORY, path)
    else:
        full_path = path
    
    return os.path.isfile(full_path)

def get_current_working_directory() -> str:
    """Returns the current working directory.
    
    Returns:
        A string representing the current working directory.
    """
    return os.getcwd()

def list_folder_tree(directory_path: str, use_data_dir: bool = True) -> List[Dict[str, Any]]:
    """Lists the contents of a directory recursively, similar to a file tree.
    
    Args:
        directory_path: The path to the directory to list. If use_data_dir is True, this should be a 
            relative path within the project data directory.
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the directory_path.
            If False, use the directory_path as provided.
            
    Returns:
        A list of dictionaries, each representing an item (file or directory) in the tree.
        Each dictionary contains 'path' (relative to the starting directory), 'type' ('file' or 'directory'),
        and optionally 'size', 'creation_time', and 'modification_time' for files.
    
    returns:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If there are permission issues when accessing the directory.
        Exception: For any other errors during directory listing or metadata retrieval.
    """
    try:
        if use_data_dir:
            full_start_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_start_path = directory_path

        if not os.path.isdir(full_start_path):
            error_msg = f"Directory not found: {full_start_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
        
        tree_structure = []
        for root, dirs, files in os.walk(full_start_path):
            relative_root = os.path.relpath(root, full_start_path)
            if relative_root == '.':
                relative_root = ''

            # Add directories
            for d in dirs:
                full_item_path = os.path.join(root, d)
                relative_item_path = os.path.join(relative_root, d)
                try:
                    stat_info = os.stat(full_item_path)
                    tree_structure.append({
                        "path": relative_item_path,
                        "type": "directory",
                        "size": stat_info.st_size,
                        "creation_time": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "modification_time": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                    })
                except Exception as e:
                    logging.warning(f"Could not retrieve metadata for directory {full_item_path}: {e}")
                    tree_structure.append({
                        "path": relative_item_path,
                        "type": "directory",
                        "error": str(e)
                    })

            # Add files
            for f in files:
                full_item_path = os.path.join(root, f)
                relative_item_path = os.path.join(relative_root, f)
                try:
                    stat_info = os.stat(full_item_path)
                    tree_structure.append({
                        "path": relative_item_path,
                        "type": "file",
                        "size": stat_info.st_size,
                        "creation_time": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "modification_time": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                    })
                except Exception as e:
                    logging.warning(f"Could not retrieve metadata for file {full_item_path}: {e}")
                    tree_structure.append({
                        "path": relative_item_path,
                        "type": "file",
                        "error": str(e)
                    })
        
        return tree_structure

    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when listing folder tree for: {directory_path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error listing folder tree for {directory_path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def get_file_permissions(path: str, use_data_dir: bool = True) -> str:
    """Gets the octal permissions of a file or directory.
    
    Args:
        path: Path to the file or directory. If use_data_dir is True, this should be a 
            relative path within the project data directory.
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        use_data_dir: If True (default), prepend the project data directory to the path.
            If False, use the path as provided.
            
    Returns:
        A string representing the octal permissions (e.g., "0o755").
        
    returns:
        FileNotFoundError: If the specified path does not exist.
        PermissionError: If there are permission issues when accessing the path.
        Exception: For any other errors during permission retrieval.
    """
    try:
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, path)
        else:
            full_path = path

        if not os.path.exists(full_path):
            error_msg = f"Path not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
            
        permissions = oct(os.stat(full_path).st_mode & 0o777)
        return permissions
    except FileNotFoundError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when getting permissions for: {path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error getting permissions for {path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def set_file_permissions(path: str, permissions_octal: str, use_data_dir: bool = True) -> str:
    """Sets the octal permissions of a file or directory.
    
    Args:
        path: Path to the file or directory. If use_data_dir is True, this should be a 
            relative path within the project data directory.
            If use_data_dir is False, this should be a full path or a path relative to 
            the current working directory.
        permissions_octal: A string representing the octal permissions (e.g., "0o755").
        use_data_dir: If True (default), prepend the project data directory to the path.
            If False, use the path as provided.
            
    Returns:
        A success message confirming the permission change.
        
    returns:
        FileNotFoundError: If the specified path does not exist.
        ValueError: If the permissions_octal string is not a valid octal number.
        PermissionError: If there are permission issues when setting permissions for the path.
        Exception: For any other errors during permission setting.
    """
    try:
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, path)
        else:
            full_path = path

        if not os.path.exists(full_path):
            error_msg = f"Path not found: {full_path}"
            logging.warning(error_msg)
            return FileNotFoundError(error_msg)
            
        # Convert octal string to integer
        try:
            mode = int(permissions_octal, 8)
        except ValueError:
            error_msg = f"Invalid octal permissions string: {permissions_octal}"
            logging.error(error_msg)
            return ValueError(error_msg)
            
        os.chmod(full_path, mode)
        return f"Successfully set permissions for {full_path} to {permissions_octal}"
    except FileNotFoundError as e:
        return e
    except ValueError as e:
        return e
    except PermissionError:
        error_msg = f"Permission denied when setting permissions for: {path}"
        logging.error(error_msg)
        return PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error setting permissions for {path}: {str(e)}"
        logging.error(error_msg)
        return Exception(e)

def filter_file_content(file_path: str, filter_pattern: str, use_regex: bool = False, case_sensitive: bool = False, include_line_numbers:  bool = False, use_data_dir: bool = True) -> Dict[str, Any]:
    """use_data_dir: If True (default), prepend the project data directory to the directory_path.
            If False, use the directory_path as provided.
    
    Returns:
        A dictionary containing:
        - 'operation': The operation performed
        - 'directory': The starting directory
        - 'pattern': The pattern used for matching
        - 'matched_files': List of files that matched the pattern
        - 'results': Results of the operation
        - 'dry_run': Whether this was a simulation
    """
    try:
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_path = directory_path
        
        # Check if the directory exists
        if not os.path.isdir(full_path):
            error_msg = f"Directory not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Validate operation
        valid_operations = ['count', 'list', 'delete', 'backup']
        if operation not in valid_operations:
            error_msg = f"Invalid operation: {operation}. Must be one of: {', '.join(valid_operations)}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Prepare regex pattern if using regex
        if use_regex:
            regex_pattern = re.compile(pattern)
        
        # Function to check if a file matches the pattern
        def file_matches(filepath):
            filename = os.path.basename(filepath)
            if use_regex:
                return bool(regex_pattern.search(filename))
            else:
                # Use glob-style matching
                import fnmatch
                return fnmatch.fnmatch(filename, pattern)
        
        # Walk through the directory recursively
        matched_files = []
        results = {}
        current_depth = 0
        
        for root, dirs, files in os.walk(full_path):
            # Check depth limit
            relative_root = os.path.relpath(root, full_path)
            current_depth = 0 if relative_root == '.' else relative_root.count(os.sep) + 1
            
            if max_depth is not None and current_depth > max_depth:
                dirs[:] = []  # Stop descending into subdirectories
                continue
            
            # Process files in this directory
            for file in files:
                file_path = os.path.join(root, file)
                
                if file_matches(file_path):
                    matched_files.append(file_path)
                    
                    # Perform the operation
                    if operation == 'delete':
                        if not dry_run:
                            try:
                                os.remove(file_path)
                                results[file_path] = "Deleted"
                            except Exception as e:
                                results[file_path] = f"Error: {str(e)}"
                        else:
                            results[file_path] = "Would be deleted (dry run)"
                    
                    elif operation == 'backup':
                        backup_path = f"{file_path}.bak"
                        if not dry_run:
                            try:
                                shutil.copy2(file_path, backup_path)
                                results[file_path] = f"Backed up to {backup_path}"
                            except Exception as e:
                                results[file_path] = f"Error: {str(e)}"
                        else:
                            results[file_path] = f"Would be backed up to {backup_path} (dry run)"
        
        # Summarize the operation
        summary = {
            'operation': operation,
            'directory': full_path,
            'pattern': pattern,
            'matched_files': matched_files,
            'total_matches': len(matched_files),
            'results': results,
            'dry_run': dry_run
        }
        
        # Add operation-specific summary
        if operation == 'count':
            summary['count'] = len(matched_files)
        
        return summary
        
    except Exception as e:
        error_msg = f"Error performing recursive operation: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def get_disk_usage(path: Optional[str] = None, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Shows available space and usage statistics for the specified path or current working directory.
    
    Args:
        path: Path to get disk usage for. If None, uses the current working directory.
            If use_data_dir is True, this should be a relative path within the project data directory.
        use_data_dir: If True (default), prepend the project data directory to the path.
            If False, use the path as provided.
    
    Returns:
        A dictionary containing disk usage statistics including:
        - 'path': The path being analyzed
        - 'total_space': Total disk space in bytes
        - 'used_space': Used disk space in bytes
        - 'free_space': Free disk space in bytes
        - 'usage_percent': Percentage of disk space used
        - 'formatted': Human-readable versions of the above values
    """
    try:
        # Determine the path to analyze
        if path is None:
            if use_data_dir:
                target_path = PROJECT_DATA_DIRECTORY
            else:
                target_path = os.getcwd()
        else:
            if use_data_dir:
                target_path = os.path.join(PROJECT_DATA_DIRECTORY, path)
            else:
                target_path = path
        
        # Get disk usage statistics
        disk_usage = psutil.disk_usage(target_path)
        
        # Format values for human readability
        def format_bytes(bytes_value):
            """Convert bytes to human-readable format"""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_value < 1024 or unit == 'TB':
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024
        
        return {
            'path': target_path,
            'total_space': disk_usage.total,
            'used_space': disk_usage.used,
            'free_space': disk_usage.free,
            'usage_percent': disk_usage.percent,
            'formatted': {
                'total_space': format_bytes(disk_usage.total),
                'used_space': format_bytes(disk_usage.used),
                'free_space': format_bytes(disk_usage.free),
                'usage_percent': f"{disk_usage.percent}%"
            }
        }
    
    except Exception as e:
        error_msg = f"Error getting disk usage for {path}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

# File versioning system - storage dictionary for versions
_file_versions = {}

def file_versioning(file_path: str, action: str = "save", version_name: Optional[str] = None, restore_version: Optional[str] = None, list_all: bool = False, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Tracks changes and maintains file history through a versioning system.
    
    Args:
        file_path: Path to the file to version. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        action: Action to perform. Must be one of: 'save' (default), 'restore', 'list', 'compare'.
        version_name: Optional name for the version being saved. If None, a timestamp will be used.
        restore_version: Version to restore (required when action is 'restore').
        list_all: If True and action is 'list', includes file content in the listing.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A dictionary containing:
        - 'file_path': The file path being versioned
        - 'action': The action performed
        - 'result': Result of the action (version saved, restored, list of versions, etc.)
    """
    try:
        global _file_versions
        
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file exists for all actions except restore (which might create the file)
        if action != 'restore' and not os.path.isfile(full_path):
            error_msg = f"File not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Initialize versioning for this file if not already done
        if full_path not in _file_versions:
            _file_versions[full_path] = {}
        
        # Perform the requested action
        if action == "save":
            # Read the current file content
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Generate version name if not provided
            if not version_name:
                version_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save the version
            _file_versions[full_path][version_name] = {
                'timestamp': datetime.now().isoformat(),
                'content': content
            }
            
            return {
                'file_path': full_path,
                'action': 'save',
                'result': f"Version '{version_name}' saved successfully",
                'version_name': version_name,
                'timestamp': _file_versions[full_path][version_name]['timestamp']
            }
        
        elif action == "restore":
            # Check if the version exists
            if not restore_version or restore_version not in _file_versions[full_path]:
                available_versions = list(_file_versions[full_path].keys())
                error_msg = f"Version '{restore_version}' not found. Available versions: {available_versions}"
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Restore the file from the specified version
            content = _file_versions[full_path][restore_version]['content']
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the content back to the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'file_path': full_path,
                'action': 'restore',
                'result': f"Version '{restore_version}' restored successfully",
                'version_name': restore_version,
                'timestamp': _file_versions[full_path][restore_version]['timestamp']
            }
        
        elif action == "list":
            # List all versions for this file
            versions = []
            for ver_name, ver_info in _file_versions[full_path].items():
                version_data = {
                    'name': ver_name,
                    'timestamp': ver_info['timestamp']
                }
                if list_all:
                    version_data['content'] = ver_info['content']
                versions.append(version_data)
            
            versions.sort(key=lambda x: x['timestamp'], reverse=True)  # Sort by timestamp (newest first)
            
            return {
                'file_path': full_path,
                'action': 'list',
                'result': f"{len(versions)} versions found",
                'versions': versions
            }
        
        elif action == "compare":
            # Need to have at least two versions to compare
            if len(_file_versions[full_path]) < 2:
                error_msg = f"Need at least two versions to compare. Only {len(_file_versions[full_path])} versions available."
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Get the two most recent versions
            versions = sorted(_file_versions[full_path].items(), 
                             key=lambda x: x[1]['timestamp'], reverse=True)
            
            latest_version = versions[0]
            previous_version = versions[1]
            
            # Compare the contents
            import difflib
            diff = list(difflib.unified_diff(
                previous_version[1]['content'].splitlines(),
                latest_version[1]['content'].splitlines(),
                fromfile=f"Version: {previous_version[0]}",
                tofile=f"Version: {latest_version[0]}",
                lineterm=''
            ))
            
            return {
                'file_path': full_path,
                'action': 'compare',
                'result': f"Compared versions '{previous_version[0]}' and '{latest_version[0]}'",
                'diff': diff,
                'from_version': previous_version[0],
                'to_version': latest_version[0]
            }
        
        else:
            error_msg = f"Invalid action: {action}. Must be one of: 'save', 'restore', 'list', 'compare'"
            logging.warning(error_msg)
            return {"error": error_msg}
        
    except Exception as e:
        error_msg = f"Error in file versioning: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

# File change detection - tracking files and their last modification times
_tracked_files = {}

def detect_file_changes(directory_path: str, action: str = "scan", pattern: str = "*", use_regex: bool = False, recursive: bool = True, max_depth: Optional[int] = None, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Identifies files that have changed since a previous scan.
    
    Args:
        directory_path: Path to the directory to monitor. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        action: Action to perform. Must be one of: 'scan' (default), 'check', 'reset'.
        pattern: Pattern to match files against. Can be a glob pattern (default: "*") or regex if use_regex is True.
        use_regex: If True, treat pattern as a regular expression. If False (default), treat as a glob pattern.
        recursive: If True (default), scan subdirectories recursively.
        max_depth: Maximum recursion depth for recursive scans. None (default) means no limit.
        use_data_dir: If True (default), prepend the project data directory to the directory_path.
            If False, use the directory_path as provided.
    
    Returns:
        A dictionary containing:
        - 'directory': The directory being monitored
        - 'action': The action performed
        - 'files_tracked': Number of files being tracked
        - 'changed_files': List of files that have changed since the last scan (for 'check' action)
        - 'new_files': List of new files found (for 'check' action)
        - 'deleted_files': List of files that have been deleted (for 'check' action)
    """
    try:
        global _tracked_files
        
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_path = directory_path
        
        # Check if the directory exists
        if not os.path.isdir(full_path):
            error_msg = f"Directory not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Function to collect files and their modification times
        def collect_files():
            collected_files = {}
            
            # Prepare regex pattern if using regex
            if use_regex:
                regex_pattern = re.compile(pattern)
            
            # Function to check if a file matches the pattern
            def file_matches(filepath):
                filename = os.path.basename(filepath)
                if use_regex:
                    return bool(regex_pattern.search(filename))
                else:
                    # Use glob-style matching
                    import fnmatch
                    return fnmatch.fnmatch(filename, pattern)
            
            # Walk through the directory
            if recursive:
                for root, _, files in os.walk(full_path):
                    # Check depth limit
                    if max_depth is not None:
                        relative_root = os.path.relpath(root, full_path)
                        current_depth = 0 if relative_root == '.' else relative_root.count(os.sep) + 1
                        if current_depth > max_depth:
                            continue
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_matches(file_path):
                            collected_files[file_path] = os.path.getmtime(file_path)
            else:
                # Non-recursive, just check the current directory
                for item in os.listdir(full_path):
                    item_path = os.path.join(full_path, item)
                    if os.path.isfile(item_path) and file_matches(item_path):
                        collected_files[item_path] = os.path.getmtime(item_path)
            
            return collected_files
        
        # Perform the requested action
        if action == "scan":
            # Scan and record the current state
            _tracked_files[full_path] = collect_files()
            
            return {
                'directory': full_path,
                'action': 'scan',
                'files_tracked': len(_tracked_files[full_path]),
                'tracked_files': list(_tracked_files[full_path].keys())
            }
        
        elif action == "check":
            # First check if we have a previous scan
            if full_path not in _tracked_files:
                return {
                    'directory': full_path,
                    'action': 'check',
                    'result': "No previous scan found. Perform a 'scan' action first.",
                    'files_tracked': 0
                }
            
            # Get current files
            current_files = collect_files()
            
            # Find changed files
            changed_files = []
            for file_path, mod_time in current_files.items():
                if file_path in _tracked_files[full_path]:
                    if mod_time > _tracked_files[full_path][file_path]:
                        changed_files.append(file_path)
            
            # Find new files
            new_files = [f for f in current_files if f not in _tracked_files[full_path]]
            
            # Find deleted files
            deleted_files = [f for f in _tracked_files[full_path] if f not in current_files]
            
            # Update the tracked files
            _tracked_files[full_path] = current_files
            
            return {
                'directory': full_path,
                'action': 'check',
                'files_tracked': len(current_files),
                'changed_files': changed_files,
                'new_files': new_files,
                'deleted_files': deleted_files,
                'total_changes': len(changed_files) + len(new_files) + len(deleted_files)
            }
        
        elif action == "reset":
            # Reset tracking for this directory
            if full_path in _tracked_files:
                del _tracked_files[full_path]
            
            return {
                'directory': full_path,
                'action': 'reset',
                'result': f"Tracking reset for directory: {full_path}"
            }
        
        else:
            error_msg = f"Invalid action: {action}. Must be one of: 'scan', 'check', 'reset'"
            logging.warning(error_msg)
            return {"error": error_msg}
        
    except Exception as e:
        error_msg = f"Error detecting file changes: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

# Store active file system observers
_active_observers = {}

# Custom file system event handler class
class CustomFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, callback_fn):
        self.callback_fn = callback_fn
        self.events = []
        
    def on_any_event(self, event):
        if event.is_directory:
            return
        
        event_info = {
            'type': event.event_type,
            'path': event.src_path,
            'is_directory': event.is_directory,
            'timestamp': datetime.now().isoformat()
        }
        
        # If it's a moved or renamed event, add the destination path
        if hasattr(event, 'dest_path'):
            event_info['dest_path'] = event.dest_path
        
        self.events.append(event_info)
        if self.callback_fn:
            self.callback_fn(event_info)

def watch_directory(directory_path: str, action: str = "start", observer_id: Optional[str] = None, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Monitors a directory for changes and file system events.
    
    Args:
        directory_path: Path to the directory to monitor. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        action: Action to perform. Must be one of: 'start' (default), 'stop', 'events', 'list'.
        observer_id: ID for the observer. Required for 'stop' and 'events' actions.
            If not provided for 'start', a unique ID will be generated.
        use_data_dir: If True (default), prepend the project data directory to the directory_path.
            If False, use the directory_path as provided.
    
    Returns:
        A dictionary containing:
        - 'directory': The directory being monitored
        - 'action': The action performed
        - 'observer_id': The ID of the observer (for 'start' action)
        - 'events': List of file system events detected (for 'events' action)
        - 'observers': List of active observers (for 'list' action)
    """
    try:
        global _active_observers
        
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_path = directory_path
        
        # Handle the list action first (doesn't require directory check)
        if action == "list":
            observers = []
            for obs_id, obs_info in _active_observers.items():
                observers.append({
                    'id': obs_id,
                    'directory': obs_info['directory'],
                    'started_at': obs_info['started_at'],
                    'event_count': len(obs_info['handler'].events)
                })
            
            return {
                'action': 'list',
                'active_observers': len(observers),
                'observers': observers
            }
        
        # Check if the directory exists for other actions
        if not os.path.isdir(full_path):
            error_msg = f"Directory not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Perform the requested action
        if action == "start":
            # Generate a unique ID if not provided
            if not observer_id:
                observer_id = f"obs_{int(datetime.now().timestamp())}_{len(_active_observers)}"
            
            # Check if observer already exists with this ID
            if observer_id in _active_observers:
                error_msg = f"Observer with ID '{observer_id}' already exists"
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Create and start the observer
            event_handler = CustomFileSystemEventHandler(None)  # No callback for now
            observer = Observer()
            observer.schedule(event_handler, full_path, recursive=True)
            observer.start()
            
            # Store the observer
            _active_observers[observer_id] = {
                'observer': observer,
                'handler': event_handler,
                'directory': full_path,
                'started_at': datetime.now().isoformat()
            }
            
            return {
                'directory': full_path,
                'action': 'start',
                'observer_id': observer_id,
                'result': f"Observer started for directory: {full_path}"
            }
        
        elif action == "stop":
            # Check if the observer exists
            if not observer_id or observer_id not in _active_observers:
                error_msg = f"Observer with ID '{observer_id}' not found"
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Stop the observer
            observer_info = _active_observers[observer_id]
            observer_info['observer'].stop()
            observer_info['observer'].join()  # Wait for the thread to finish
            
            # Collect the events
            events = observer_info['handler'].events
            
            # Remove the observer
            del _active_observers[observer_id]
            
            return {
                'directory': observer_info['directory'],
                'action': 'stop',
                'observer_id': observer_id,
                'result': f"Observer stopped for directory: {observer_info['directory']}",
                'events': events,
                'event_count': len(events)
            }
        
        elif action == "events":
            # Check if the observer exists
            if not observer_id or observer_id not in _active_observers:
                error_msg = f"Observer with ID '{observer_id}' not found"
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Get the events without stopping the observer
            events = _active_observers[observer_id]['handler'].events
            
            return {
                'directory': _active_observers[observer_id]['directory'],
                'action': 'events',
                'observer_id': observer_id,
                'events': events,
                'event_count': len(events)
            }
        
        else:
            error_msg = f"Invalid action: {action}. Must be one of: 'start', 'stop', 'events', 'list'"
            logging.warning(error_msg)
            return {"error": error_msg}
        
    except Exception as e:
        error_msg = f"Error watching directory {directory_path}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def search_file_content(file_path: str, search_text: str, use_regex: bool = False, case_sensitive: bool = True, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Searches file content for specific text or patterns.
    
    Args:
        file_path: Path to the file to search. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        search_text: The text or pattern to search for in the file.
        use_regex: If True, treat search_text as a regular expression. If False (default),
            treat it as a plain text pattern.
        case_sensitive: If True (default), perform case-sensitive search. If False, 
            perform case-insensitive search.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A dictionary containing:
        - 'file_path': The full path to the searched file
        - 'matches_found': Number of matches found
        - 'matched_lines': A list of dictionaries, each containing 'line_number' and 'line_content'
    """
    try:
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            error_msg = f"File not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Prepare regex pattern based on parameters
        if not use_regex:
            # Escape special regex characters if not using regex mode
            search_text = re.escape(search_text)
        
        # Set regex flags
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(search_text, flags)
        
        # Search the file content
        matched_lines = []
        matches_found = 0
        
        with open(full_path, 'r', encoding='utf-8', errors='replace') as file:
            for line_number, line in enumerate(file, 1):
                match = pattern.search(line)
                if match:
                    matches_found += 1
                    matched_lines.append({
                        'line_number': line_number,
                        'line_content': line.rstrip('\n'),
                        'match_position': match.span()
                    })
        
        return {
            'file_path': full_path,
            'search_text': search_text,
            'matches_found': matches_found,
            'matched_lines': matched_lines
        }
        
    except Exception as e:
        error_msg = f"Error searching file {file_path}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def set_working_directory(new_directory: str) -> Dict[str, Any]:
    """
    Sets the working directory for file operations. This changes the base directory used when use_data_dir=True.
    
    Args:
        new_directory: The new directory path to use as the working directory. This should be an absolute path.
            If the path doesn't exist, it will be created.
    
    Returns:
        A dictionary with the status and the updated working directory path.
    """
    try:
        global PROJECT_DATA_DIRECTORY
        
        # Create the directory if it doesn't exist
        if not os.path.exists(new_directory):
            os.makedirs(new_directory, exist_ok=True)
            status_message = f"Created new working directory: {new_directory}"
        else:
            # Verify it's a directory
            if not os.path.isdir(new_directory):
                return {
                    "status": "error",
                    "message": f"The path {new_directory} exists but is not a directory"
                }
            status_message = f"Using existing directory: {new_directory}"
        
        # Update the project data directory
        old_directory = PROJECT_DATA_DIRECTORY
        PROJECT_DATA_DIRECTORY = new_directory
        
        return {
            "status": "success",
            "message": status_message,
            "old_working_directory": old_directory,
            "new_working_directory": PROJECT_DATA_DIRECTORY
        }
    except Exception as e:
        error_msg = f"Error setting working directory to {new_directory}: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

def zip_files(source_paths: List[str], output_zip_path: str, compression_level: int = 9, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Compresses files or directories into a ZIP archive.
    
    Args:
        source_paths: List of paths to files/directories to include in the ZIP archive.
            If use_data_dir is True, these should be relative paths within the project data directory.
        output_zip_path: Path for the output ZIP file. If use_data_dir is True, this should be a
            relative path within the project data directory.
        compression_level: Compression level (0-9, where 9 is highest compression). Default is 9.
        use_data_dir: If True (default), prepend the project data directory to all paths.
            If False, use the paths as provided.
    
    Returns:
        A dictionary containing:
        - 'zip_path': Full path to the created ZIP file
        - 'files_added': List of files added to the archive
        - 'total_files': Number of files added
        - 'total_size': Size of the ZIP file in bytes
        - 'compressed_size': Size of the compressed data in bytes
    """
    try:
        # Get the full paths based on use_data_dir setting
        if use_data_dir:
            full_source_paths = [os.path.join(PROJECT_DATA_DIRECTORY, path) for path in source_paths]
            full_output_path = os.path.join(PROJECT_DATA_DIRECTORY, output_zip_path)
        else:
            full_source_paths = source_paths
            full_output_path = output_zip_path
        
        # Create parent directories for the output ZIP file if they don't exist
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        # Validate source paths
        valid_sources = []
        invalid_sources = []
        for path in full_source_paths:
            if os.path.exists(path):
                valid_sources.append(path)
            else:
                invalid_sources.append(path)
        
        if not valid_sources:
            error_msg = f"No valid source paths found. Invalid paths: {invalid_sources}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Collect all files to add to the ZIP
        files_to_add = []
        for source in valid_sources:
            if os.path.isfile(source):
                files_to_add.append((source, os.path.basename(source)))
            elif os.path.isdir(source):
                base_path = os.path.dirname(source)
                for root, _, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path within the ZIP file
                        arcname = os.path.relpath(file_path, base_path)
                        files_to_add.append((file_path, arcname))
        
        # Create the ZIP file
        with zipfile.ZipFile(full_output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            for file_path, arcname in files_to_add:
                zipf.write(file_path, arcname)
        
        # Get stats about the created ZIP file
        zip_size = os.path.getsize(full_output_path)
        
        # Get compressed size
        compressed_size = 0
        with zipfile.ZipFile(full_output_path, 'r') as zipf:
            for info in zipf.infolist():
                compressed_size += info.compress_size
        
        return {
            'zip_path': full_output_path,
            'files_added': [f[1] for f in files_to_add],  # List of arcnames
            'total_files': len(files_to_add),
            'total_size': zip_size,
            'compressed_size': compressed_size,
            'invalid_sources': invalid_sources if invalid_sources else None
        }
        
    except Exception as e:
        error_msg = f"Error creating ZIP file: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def extract_zip(zip_path: str, output_dir: Optional[str] = None, specific_files: Optional[List[str]] = None, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Extracts files from a ZIP archive.
    
    Args:
        zip_path: Path to the ZIP file to extract. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        output_dir: Directory to extract files to. If None, extracts to the same directory as the ZIP file.
            If use_data_dir is True, this should be a relative path within the project data directory.
        specific_files: List of specific files to extract. If None, extracts all files.
        use_data_dir: If True (default), prepend the project data directory to the paths.
            If False, use the paths as provided.
    
    Returns:
        A dictionary containing:
        - 'zip_path': Full path to the ZIP file
        - 'output_dir': Full path to the output directory
        - 'files_extracted': List of files extracted
        - 'total_files': Number of files extracted
    """
    try:
        # Get the full paths based on use_data_dir setting
        if use_data_dir:
            full_zip_path = os.path.join(PROJECT_DATA_DIRECTORY, zip_path)
            full_output_dir = os.path.join(PROJECT_DATA_DIRECTORY, output_dir) if output_dir else os.path.dirname(full_zip_path)
        else:
            full_zip_path = zip_path
            full_output_dir = output_dir if output_dir else os.path.dirname(full_zip_path)
        
        # Check if the ZIP file exists
        if not os.path.isfile(full_zip_path):
            error_msg = f"ZIP file not found: {full_zip_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Create output directory if it doesn't exist
        os.makedirs(full_output_dir, exist_ok=True)
        
        # Extract files
        files_extracted = []
        with zipfile.ZipFile(full_zip_path, 'r') as zipf:
            # Get list of files to extract
            all_files = zipf.namelist()
            to_extract = specific_files if specific_files else all_files
            
            # Validate files to extract
            invalid_files = [f for f in to_extract if f not in all_files] if specific_files else []
            valid_files = [f for f in to_extract if f in all_files] if specific_files else all_files
            
            if not valid_files:
                error_msg = f"No valid files to extract. Invalid files: {invalid_files}"
                logging.warning(error_msg)
                return {"error": error_msg}
            
            # Extract files
            for file in valid_files:
                zipf.extract(file, full_output_dir)
                files_extracted.append(file)
        
        return {
            'zip_path': full_zip_path,
            'output_dir': full_output_dir,
            'files_extracted': files_extracted,
            'total_files': len(files_extracted),
            'invalid_files': invalid_files if invalid_files else None
        }
        
    except Exception as e:
        error_msg = f"Error extracting ZIP file: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def batch_process_files(directory_path: str, operation: str, pattern: str = "*", recursive: bool = True, use_regex: bool = False, max_files: Optional[int] = None, dry_run: bool = True, operation_args: Optional[Dict[str, Any]] = None, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Processes multiple files based on patterns or rules in a single operation.
    
    Args:
        directory_path: Path to the directory containing files to process. If use_data_dir is True, 
            this should be a relative path within the project data directory.
        operation: Operation to perform on each file. Supported operations: 
            'copy', 'move', 'delete', 'rename', 'hash', 'transform'.
        pattern: Pattern to match files. Can be a glob pattern or regex depending on use_regex.
            Default is "*" (all files).
        recursive: If True (default), include files in subdirectories.
        use_regex: If True, treat the pattern as a regular expression. If False (default),
            treat it as a glob pattern.
        max_files: Maximum number of files to process. None means no limit.
        dry_run: If True (default), only simulate the operation without making changes.
        operation_args: Additional arguments for the specific operation:
            - 'copy'/'move': Requires 'destination' (target directory)
            - 'rename': Requires 'rename_pattern' (can include {index}, {name}, {ext} placeholders)
            - 'transform': Requires 'transform_function' (e.g., 'uppercase', 'lowercase', 'replace')
              and possibly 'search_text'/'replace_text' for 'replace' transform
        use_data_dir: If True (default), prepend the project data directory to the paths.
            If False, use the paths as provided.
    
    Returns:
        A dictionary containing:
        - 'operation': Operation performed
        - 'matched_files': List of files that matched the pattern
        - 'processed_files': List of files that were processed (with details)
        - 'dry_run': Whether this was a simulation
        - 'total_matches': Number of files matched
        - 'total_processed': Number of files processed
    """
    try:
        # Get the full directory path based on use_data_dir setting
        if use_data_dir:
            full_dir_path = os.path.join(PROJECT_DATA_DIRECTORY, directory_path)
        else:
            full_dir_path = directory_path
        
        # Check if the directory exists
        if not os.path.isdir(full_dir_path):
            error_msg = f"Directory not found: {full_dir_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Initialize operation arguments if None
        if operation_args is None:
            operation_args = {}
        
        # Validate operation
        valid_operations = ['copy', 'move', 'delete', 'rename', 'hash', 'transform']
        if operation not in valid_operations:
            error_msg = f"Invalid operation: {operation}. Valid operations are: {', '.join(valid_operations)}"
            logging.error(error_msg)
            return {"error": error_msg}
        
        # Validate operation-specific arguments
        if operation in ['copy', 'move'] and 'destination' not in operation_args:
            error_msg = f"Operation '{operation}' requires 'destination' argument"
            logging.error(error_msg)
            return {"error": error_msg}
        
        if operation == 'rename' and 'rename_pattern' not in operation_args:
            error_msg = "Operation 'rename' requires 'rename_pattern' argument"
            logging.error(error_msg)
            return {"error": error_msg}
        
        if operation == 'transform':
            if 'transform_function' not in operation_args:
                error_msg = "Operation 'transform' requires 'transform_function' argument"
                logging.error(error_msg)
                return {"error": error_msg}
                
            valid_transforms = ['uppercase', 'lowercase', 'replace']
            if operation_args['transform_function'] not in valid_transforms:
                error_msg = f"Invalid transform function: {operation_args['transform_function']}. Valid functions are: {', '.join(valid_transforms)}"
                logging.error(error_msg)
                return {"error": error_msg}
                
            if operation_args['transform_function'] == 'replace' and ('search_text' not in operation_args or 'replace_text' not in operation_args):
                error_msg = "Transform function 'replace' requires 'search_text' and 'replace_text' arguments"
                logging.error(error_msg)
                return {"error": error_msg}
        
        # Prepare destination directory for copy/move operations
        if operation in ['copy', 'move']:
            if use_data_dir:
                full_dest_path = os.path.join(PROJECT_DATA_DIRECTORY, operation_args['destination'])
            else:
                full_dest_path = operation_args['destination']
                
            # Create destination directory if it doesn't exist and we're not in dry run mode
            if not dry_run and not os.path.exists(full_dest_path):
                os.makedirs(full_dest_path, exist_ok=True)
        
        # Find matching files
        matched_files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, _, files in os.walk(full_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if the file matches the pattern
                    if use_regex:
                        if re.search(pattern, file):
                            matched_files.append(file_path)
                    else:  # Use glob pattern
                        import fnmatch
                        if fnmatch.fnmatch(file, pattern):
                            matched_files.append(file_path)
        else:
            # Only check files in the specified directory
            for file in os.listdir(full_dir_path):
                file_path = os.path.join(full_dir_path, file)
                
                if os.path.isfile(file_path):
                    # Check if the file matches the pattern
                    if use_regex:
                        if re.search(pattern, file):
                            matched_files.append(file_path)
                    else:  # Use glob pattern
                        import fnmatch
                        if fnmatch.fnmatch(file, pattern):
                            matched_files.append(file_path)
        
        # Apply file limit if specified
        if max_files is not None:
            matched_files = matched_files[:max_files]
        
        # Process files
        processed_files = []
        
        for index, file_path in enumerate(matched_files):
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            name, ext = os.path.splitext(file_name)
            
            result = {
                'original_path': file_path,
                'file_name': file_name,
                'operation': operation
            }
            
            # Skip actual processing if in dry run mode
            if not dry_run:
                try:
                    if operation == 'copy':
                        dest_file = os.path.join(full_dest_path, file_name)
                        shutil.copy2(file_path, dest_file)
                        result['destination'] = dest_file
                        
                    elif operation == 'move':
                        dest_file = os.path.join(full_dest_path, file_name)
                        shutil.move(file_path, dest_file)
                        result['destination'] = dest_file
                        
                    elif operation == 'delete':
                        os.remove(file_path)
                        result['status'] = 'deleted'
                        
                    elif operation == 'rename':
                        # Process rename pattern with placeholders
                        rename_pattern = operation_args['rename_pattern']
                        new_name = rename_pattern.format(
                            index=index+1,
                            name=name,
                            ext=ext[1:] if ext else ''  # Remove leading dot from extension
                        )
                        
                        # Ensure the new name has an extension if the original did
                        if ext and not os.path.splitext(new_name)[1]:
                            new_name += ext
                            
                        new_path = os.path.join(file_dir, new_name)
                        os.rename(file_path, new_path)
                        result['new_path'] = new_path
                        result['new_name'] = new_name
                        
                    elif operation == 'hash':
                        # Use specified algorithm or default to MD5
                        algorithm = operation_args.get('algorithm', 'md5')
                        hash_result = calculate_file_hash(file_path, algorithm, use_data_dir=False)  # Using full path already
                        result['hash'] = hash_result['hash']
                        result['algorithm'] = algorithm
                        
                    elif operation == 'transform':
                        transform_func = operation_args['transform_function']
                        
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        
                        # Apply transformation
                        if transform_func == 'uppercase':
                            new_content = content.upper()
                        elif transform_func == 'lowercase':
                            new_content = content.lower()
                        elif transform_func == 'replace':
                            search_text = operation_args['search_text']
                            replace_text = operation_args['replace_text']
                            new_content = content.replace(search_text, replace_text)
                        
                        # Write transformed content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                        result['transform'] = transform_func
                        result['chars_changed'] = len(content) - len(new_content)
                        
                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = str(e)
                    logging.error(f"Error processing file {file_path}: {str(e)}")
            else:
                # For dry run, add simulated result
                if operation == 'copy':
                    result['destination'] = os.path.join(full_dest_path, file_name)
                    result['status'] = 'would_copy'
                elif operation == 'move':
                    result['destination'] = os.path.join(full_dest_path, file_name)
                    result['status'] = 'would_move'
                elif operation == 'delete':
                    result['status'] = 'would_delete'
                elif operation == 'rename':
                    rename_pattern = operation_args['rename_pattern']
                    new_name = rename_pattern.format(
                        index=index+1,
                        name=name,
                        ext=ext[1:] if ext else ''  # Remove leading dot from extension
                    )
                    
                    # Ensure the new name has an extension if the original did
                    if ext and not os.path.splitext(new_name)[1]:
                        new_name += ext
                        
                    new_path = os.path.join(file_dir, new_name)
                    result['new_path'] = new_path
                    result['new_name'] = new_name
                    result['status'] = 'would_rename'
                elif operation == 'hash':
                    result['status'] = 'would_hash'
                    result['algorithm'] = operation_args.get('algorithm', 'md5')
                elif operation == 'transform':
                    result['status'] = 'would_transform'
                    result['transform'] = operation_args['transform_function']
            
            processed_files.append(result)
        
        return {
            'operation': operation,
            'pattern': pattern,
            'recursive': recursive,
            'matched_files': [os.path.basename(f) for f in matched_files],
            'processed_files': processed_files,
            'dry_run': dry_run,
            'total_matches': len(matched_files),
            'total_processed': len(processed_files)
        }
        
    except Exception as e:
        error_msg = f"Error in batch processing: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def calculate_file_hash(file_path: str, hash_algorithm: str = "md5", use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Generates a hash checksum for a file to verify file integrity.
    
    Args:
        file_path: Path to the file to hash. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        hash_algorithm: Hash algorithm to use. Options are 'md5', 'sha1', 'sha256', or 'sha512'.
            Default is 'md5'.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A dictionary containing:
        - 'file_path': Full path to the file
        - 'algorithm': Hash algorithm used
        - 'hash': The generated hash/checksum
        - 'file_size': Size of the file in bytes
    """
    try:
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            error_msg = f"File not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Validate and select hash algorithm
        hash_func = None
        if hash_algorithm.lower() == "md5":
            hash_func = hashlib.md5()
        elif hash_algorithm.lower() == "sha1":
            hash_func = hashlib.sha1()
        elif hash_algorithm.lower() == "sha256":
            hash_func = hashlib.sha256()
        elif hash_algorithm.lower() == "sha512":
            hash_func = hashlib.sha512()
        else:
            error_msg = f"Invalid hash algorithm: {hash_algorithm}. Valid options are 'md5', 'sha1', 'sha256', 'sha512'."
            logging.error(error_msg)
            return {"error": error_msg}
        
        # Calculate hash in chunks to handle large files efficiently
        file_size = os.path.getsize(full_path)
        chunk_size = 8192  # 8KB chunks
        
        with open(full_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_func.update(chunk)
        
        # Get hexadecimal digest
        file_hash = hash_func.hexdigest()
        
        return {
            'file_path': full_path,
            'algorithm': hash_algorithm.lower(),
            'hash': file_hash,
            'file_size': file_size
        }
        
    except Exception as e:
        error_msg = f"Error calculating hash for {file_path}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def compare_files(file_path1: str, file_path2: str, show_diff: bool = False, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Compares two files and identifies if they are identical or what differences exist.
    
    Args:
        file_path1: Path to the first file. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        file_path2: Path to the second file. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        show_diff: If True, includes the actual differences between files in the response.
            For large files, this can be memory intensive.
        use_data_dir: If True (default), prepend the project data directory to the file paths.
            If False, use the file paths as provided.
    
    Returns:
        A dictionary containing:
        - 'identical': Boolean indicating if the files are identical
        - 'file1': Full path to the first file
        - 'file2': Full path to the second file
        - 'comparison_type': Type of comparison performed ('binary', 'line_by_line')
        - 'differences': List of differences (if show_diff is True and files differ)
    """
    try:
        # Get the full paths based on use_data_dir setting
        if use_data_dir:
            full_path1 = os.path.join(PROJECT_DATA_DIRECTORY, file_path1)
            full_path2 = os.path.join(PROJECT_DATA_DIRECTORY, file_path2)
        else:
            full_path1 = file_path1
            full_path2 = file_path2
        
        # Check if both files exist
        if not os.path.isfile(full_path1):
            error_msg = f"First file not found: {full_path1}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        if not os.path.isfile(full_path2):
            error_msg = f"Second file not found: {full_path2}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Quick shallow comparison first (file size and signature)
        if filecmp.cmp(full_path1, full_path2, shallow=True):
            # Files appear identical in shallow comparison
            return {
                'identical': True,
                'file1': full_path1,
                'file2': full_path2,
                'comparison_type': 'binary',
                'message': "Files are identical (binary comparison)"
            }
        
        # Files differ - if we need details, do a line-by-line comparison
        result = {
            'identical': False,
            'file1': full_path1,
            'file2': full_path2,
            'comparison_type': 'binary',
            'message': "Files are different"
        }
        
        if show_diff:
            # Try to do a line-by-line text comparison
            try:
                result['comparison_type'] = 'line_by_line'
                differences = []
                
                with open(full_path1, 'r', encoding='utf-8', errors='replace') as f1, \
                     open(full_path2, 'r', encoding='utf-8', errors='replace') as f2:
                    lines1 = f1.readlines()
                    lines2 = f2.readlines()
                
                # Find differences
                for i, (line1, line2) in enumerate(zip(lines1, lines2)):
                    if line1 != line2:
                        differences.append({
                            'line_number': i + 1,
                            'file1_line': line1.rstrip('\n'),
                            'file2_line': line2.rstrip('\n')
                        })
                
                # Handle case where files have different number of lines
                if len(lines1) > len(lines2):
                    for i in range(len(lines2), len(lines1)):
                        differences.append({
                            'line_number': i + 1,
                            'file1_line': lines1[i].rstrip('\n'),
                            'file2_line': "[No line]"
                        })
                elif len(lines2) > len(lines1):
                    for i in range(len(lines1), len(lines2)):
                        differences.append({
                            'line_number': i + 1,
                            'file1_line': "[No line]",
                            'file2_line': lines2[i].rstrip('\n')
                        })
                
                result['differences'] = differences
                result['diff_count'] = len(differences)
                result['file1_lines'] = len(lines1)
                result['file2_lines'] = len(lines2)
                
            except UnicodeDecodeError:
                # If we can't do a text comparison, fall back to binary
                result['comparison_type'] = 'binary'
                result['message'] = "Files are different (binary files cannot show line differences)"
        
        return result
        
    except Exception as e:
        error_msg = f"Error comparing files {file_path1} and {file_path2}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

def get_file_metadata(file_path: str, use_data_dir: bool = True) -> Dict[str, Any]:
    """
    Gets detailed metadata about a file including creation time, modification time, access time, size, etc.
    
    Args:
        file_path: Path to the file to get metadata for. If use_data_dir is True, this should be a 
            relative path within the project data directory.
        use_data_dir: If True (default), prepend the project data directory to the file_path.
            If False, use the file_path as provided.
    
    Returns:
        A dictionary containing detailed file metadata including:
        - 'name': File name without path
        - 'path': Full path to the file
        - 'size': Size in bytes
        - 'size_human': Human-readable size (e.g., "2.5 MB")
        - 'created': Creation timestamp
        - 'modified': Last modification timestamp
        - 'accessed': Last access timestamp
        - 'is_file': Boolean indicating if it's a file
        - 'is_dir': Boolean indicating if it's a directory
        - 'is_symlink': Boolean indicating if it's a symbolic link
        - 'extension': File extension (if applicable)
        - 'permissions': File permissions in octal format
        - 'owner': Owner of the file (if available)
        - 'group': Group of the file (if available)
    """
    try:
        # Get the full path based on use_data_dir setting
        if use_data_dir:
            full_path = os.path.join(PROJECT_DATA_DIRECTORY, file_path)
        else:
            full_path = file_path
        
        # Check if the path exists
        if not os.path.exists(full_path):
            error_msg = f"Path not found: {full_path}"
            logging.warning(error_msg)
            return {"error": error_msg}
        
        # Get file stats
        file_stat = os.stat(full_path)
        file_info = Path(full_path)
        
        # Get human-readable size
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        
        # Try to get owner and group (platform dependent)
        owner = ""
        group = ""
        try:
            if platform.system() != "Windows":
                # Unix-like systems
                owner = pwd.getpwuid(file_stat.st_uid).pw_name
                group = grp.getgrgid(file_stat.st_gid).gr_name
            else:
                # Windows systems - these details aren't easily accessible
                import ctypes
                try:
                    # Try to get owner using Windows API, but may not always work
                    owner = "N/A (Windows)"
                    group = "N/A (Windows)"
                except:
                    owner = "N/A (Windows)"
                    group = "N/A (Windows)"
        except Exception as e:
            # Fallback to numeric IDs
            owner = str(file_stat.st_uid)
            group = str(file_stat.st_gid)
        
        # Build metadata dictionary
        metadata = {
            'name': os.path.basename(full_path),
            'path': full_path,
            'size': file_stat.st_size,
            'size_human': format_size(file_stat.st_size),
            'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(file_stat.st_atime).isoformat(),
            'is_file': os.path.isfile(full_path),
            'is_dir': os.path.isdir(full_path),
            'is_symlink': os.path.islink(full_path),
            'extension': os.path.splitext(full_path)[1].lstrip('.') if os.path.isfile(full_path) else '',
            'permissions': oct(file_stat.st_mode)[-3:],  # Last 3 digits of octal representation
            'permissions_full': oct(file_stat.st_mode),
            'owner': owner,
            'group': group
        }
        
        return metadata
        
    except Exception as e:
        error_msg = f"Error getting metadata for {file_path}: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}

