# Multi-Agent Assistant with MCP Tools

A versatile AI assistant platform built with Google's Agent Development Kit (ADK) that combines specialized agents with Model Context Protocol (MCP) tools for enhanced capabilities.

## Overview

This project implements a multi-agent system using Google's Agent Development Kit (ADK). The system consists of a coordinator agent that delegates tasks to specialized sub-agents based on the user's needs. It features robust integration with Model Context Protocol (MCP) tools and includes Windows compatibility fixes.

## Key Features

- **Coordinator Architecture**: Central agent that directs requests to specialized sub-agents
- **Specialized Agents**:
  - **LinkedIn Writer**: Creates professional LinkedIn posts with image prompts
  - **Resume Writer**: Generates ATS-optimized resumes
  - **Python Agent**: Handles code generation and data analysis
- **MCP Tools Integration**:
  - Windows-compatible implementation
  - Google Maps functionality with fallback mechanisms
  - Web page content extraction and analysis
- **Robust State Management**: Maintains context across agent interactions
- **User Interaction**: Interactive decision-making through choice presentation

## Technical Architecture

### Agent Structure

```
Coordinator Agent
├── LinkedIn Writer Agent
├── Resume Writer Agent
├── Python Agent
├── Google Search Tool
└── MCP Tools (Maps, Web Page Loader, etc.)
```

### Implementation Details

- **Framework**: Google ADK (Agent Development Kit)
- **Models**: Gemini models for all agents
- **MCP Implementation**: Dynamic tool selection with fallback mechanisms
- **Cross-Platform**: Works on both Windows and Unix-based systems
- **Error Handling**: Graceful degradation when services are unavailable

## Installation

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Google API Key (for Gemini models)
- Google Maps API Key (optional, for location features)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd my-awesome-agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Using venv
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using Poetry
   poetry install
   ```

4. **Environment configuration**:
   
   Create a `.env` file in the project root with the following variables:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   GOOGLE_MAPS_API_KEY=your_maps_api_key_here
   LINKEDIN_MODEL=gemini-1.5-pro-latest
   ```

## Running the Application

### Local Development

1. **Start the ADK web interface**:
   ```bash
   adk web
   ```

2. **Start the API server** (in a separate terminal):
   ```bash
   adk api_server --allow_origins="http://localhost:4200"
   ```

3. **Access the interface** at `http://localhost:4200`

### MCP Tools Setup (Optional)

For full MCP functionality:

1. **Windows Users**:
   - Use the built-in fallback mechanisms (already implemented)
   - Or, for better performance, consider using Windows Subsystem for Linux (WSL)

2. **MCP Server URLs** (if manually configuring):
   - Google Maps: `http://localhost:8082`
   - Default: `http://localhost:8080`

## Usage Examples

### LinkedIn Content Creation

```
User: Create a LinkedIn post about artificial intelligence in healthcare
Agent: *Researches current trends in AI healthcare*
       *Generates professional LinkedIn post with complementary image prompt*
```

### Resume Generation

```
User: I need a resume for a software engineer with 5 years of experience
Agent: *Creates ATS-optimized resume tailored to software engineering roles*
```

### Location-Based Queries

```
User: What coffee shops are near Central Park in NYC?
Agent: *Uses Google Maps integration to find and list coffee shops*
```

### Web Research

```
User: Summarize the latest developments in quantum computing
Agent: *Performs web searches and analyzes content from relevant pages*
       *Provides structured summary of findings*
```

## Extending the System

### Adding New Agents

1. Define a new agent in `agent.py` with appropriate tools and instructions
2. Create a specialized prompt in `prompt.py`
3. Register the agent as a tool in the coordinator agent

### Integrating Additional MCP Tools

1. Add new MCP server URLs in the `get_mcp_server_url` function
2. Implement custom fallback tools for Windows compatibility
3. Update the coordinator prompt to include descriptions of new tools

## Troubleshooting

- **MCP Tools on Windows**: If you encounter `NotImplementedError` related to subprocess handling, the system will automatically use fallback mechanisms.
- **Missing Dependencies**: Ensure BeautifulSoup and lxml are installed for web page content extraction.
- **API Key Issues**: Verify all required API keys are correctly set in your `.env` file.

## Project Structure

```
my-awesome-agent/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Agent definitions and MCP integration
│   ├── prompt.py            # Agent instructions and prompts
│   ├── tools.py             # Custom tool implementations
│   ├── callbacks.py         # Callback implementations
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── .env                     # Environment variables (not in version control)
├── .gitignore               # Git ignore configuration
├── requirements.txt         # Dependencies
├── pyproject.toml           # Poetry configuration
└── README.md                # This documentation
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Built with [Google's Agent Development Kit](https://github.com/google/adk)
- Powered by [Gemini](https://deepmind.google/technologies/gemini/) language models
- Developed by Team SONGOKU