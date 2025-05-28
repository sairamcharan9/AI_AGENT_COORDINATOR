"""Resume Writer Agent implementation."""

import os
from google.adk.agents import LlmAgent
from typing import Dict, Any

from google.adk.tools import google_search
from .prompt import RESUME_WRITER_PROMPT

# Get model from environment
# Resume writer agent specific model, falls back to main MODEL if not specified
RESUME_MODEL = os.getenv("RESUME_MODEL", os.getenv("MODEL", "gemini-2.5-flash-preview-05-20"))

# Resume Writer Agent (Creates professional, ATS-optimized resumes)
resume_writer_agent = LlmAgent(
    name="ResumeWriter",
    model=RESUME_MODEL,
    instruction=RESUME_WRITER_PROMPT, 
    tools = [google_search],# Use built-in Google search directly
    description="Creates professional, ATS-optimized resumes tailored to specific industries and job targets.",
    output_key="resume_output"
)
