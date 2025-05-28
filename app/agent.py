import os
import json
import logging
import shutil
from typing import Dict, Any

from google.adk.agents import LlmAgent,Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import load_artifacts, load_memory, get_user_choice, transfer_to_agent
from google.adk.tools import google_search
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools import ToolContext
from google.adk.tools import LongRunningFunctionTool
from google.adk.code_executors import VertexAiCodeExecutor
from .tools import *
from dotenv import load_dotenv
from . import prompt
from .utils.utils import get_image_bytes,get_env_var
# Import sub-agents from their respective modules
from .SUB_AGENTS.LinkedIN_Agent.agent import linkedin_agent
from .SUB_AGENTS.Resume_Agent.agent import resume_writer_agent
from .SUB_AGENTS.PythonAgent.agent import python_agent
from .SUB_AGENTS.file_handler_agent.agent import file_handler_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get model from environment
# Main coordinator model
MODEL = os.getenv("MODEL", "gemini-2.5-flash-preview-05-20")


google_search_agent = LlmAgent(
    name="google_search_assistant",
    model=MODEL,
    description=(
        "You Help with Google Search"
    ),
    instruction="""You help with google search give descriptive results, up-to-date relevant information, include one or two urls to websites""",
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
    
def generate_image(img_prompt: str, folder_name: str, file_name: str, tool_context: ToolContext):
    """Generates an image based on the prompt and saves it to a specified file path."""
    response = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=img_prompt,
        config={"number_of_images": 1},
    )

    if not response.generated_images:
        return {"status": "failed", "detail": "Image generation failed: No image bytes returned."}

    image_bytes = response.generated_images[0].image.image_bytes
    
    # Save the image as an artifact using the tool_context
    # Consider if 'file_name' should be passed here instead of a generic 'image.png'
    tool_context.save_artifact(
        file_name, # Changed from "image.png" to use the dynamic file_name
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    )

    # Construct the full file path where the image will be saved on disk
    # Assuming 'app/utils/data' is the base for your project's data files
    base_data_path = "app/utils/data"
    full_folder_path = os.path.join(base_data_path, folder_name)
    full_file_path = os.path.join(full_folder_path, file_name)

    # Ensure the target directory exists before writing the file
    # 'exist_ok=True' prevents an error if the directory already exists
    os.makedirs(full_folder_path, exist_ok=True)

    # Write the image bytes to the file in binary write mode ('wb')
    with open(full_file_path, "wb") as f:
        f.write(image_bytes)

    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts and on disk.",
        "filename": file_name,
        "filepath": full_file_path, # Provide the full path where the file was saved
    }

# Create Agent Tools for the coordinator
linkedin_agent_tool = AgentTool(agent=linkedin_agent)
resume_writer_agent_tool = AgentTool(agent=resume_writer_agent)
python_agent_tool = AgentTool(agent=python_agent)
file_handler_agent_tool = AgentTool(agent=file_handler_agent)

# Coordinator agent that allows flexible usage of components
my_coordinator = Agent(
    name="my_coordinator",
    model=MODEL,
    instruction=prompt.MY_COORDINATOR_PROMPT,  # Using existing coordinator prompt
    sub_agents=[resume_writer_agent],
    tools=[
        call_google_tool,
        linkedin_agent_tool,
        file_handler_agent_tool,
        generate_image,
        load_artifacts,
        python_agent_tool,
        load_memory,
        get_user_choice,
        get_image_bytes,
        get_env_var,
    ]
)

# Set the root agent to be the coordinator for maximum flexibility
root_agent = my_coordinator