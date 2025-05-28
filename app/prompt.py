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

"""Prompts for the Multi-Agent System.

This file is maintained for backward compatibility.
All prompts have been moved to their respective module files.
"""

# Import prompts from their respective modules for backward compatibility
from .SUB_AGENTS.LinkedIN_Agent.prompt import LINKEDIN_AGENT_PROMPT
from .SUB_AGENTS.Resume_Agent.prompt import RESUME_WRITER_PROMPT
from .SUB_AGENTS.PythonAgent.prompt import PYTHON_AGENT_PROMPT
from .coordinator_prompt import MY_COORDINATOR_PROMPT
from .SUB_AGENTS.file_handler_agent.prompt import FILE_HANDLER_AGENT_PROMPT

__all__ = [
    "LINKEDIN_AGENT_PROMPT", 
    "RESUME_WRITER_PROMPT",
    "PYTHON_AGENT_PROMPT",
    "MY_COORDINATOR_PROMPT",
    "FILE_HANDLER_AGENT_PROMPT"
]
