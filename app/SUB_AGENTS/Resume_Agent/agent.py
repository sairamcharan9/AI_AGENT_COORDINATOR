"""Resume Writer Agent implementation."""

import os
from google.adk.agents import LlmAgent
from typing import Dict, Any

from google.adk.tools import google_search
from .prompt import RESUME_WRITER_PROMPT

# Get model from environment
MODEL = os.getenv("LINKEDIN_MODEL", "gemini-2.5-pro-preview-05-06")

# Resume Writer Agent (Creates professional, ATS-optimized resumes)
resume_writer_agent = LlmAgent(
    name="ResumeWriter",
    model=MODEL,
    instruction=RESUME_WRITER_PROMPT, 
    tools = [google_search],# Use built-in Google search directly
    description="Creates professional, ATS-optimized resumes tailored to specific industries and job targets.",
    output_key="resume_output"
)
