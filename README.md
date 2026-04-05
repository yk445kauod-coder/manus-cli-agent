# Manus CLI Agent 🚀

A fast, powerful AI CLI agent inspired by Claude Code, built with **MCP (Model Context Protocol)** and **SKILL.md** system.

Developed by: **Yousef Khamis**

## Features
- ⚡ **Faster than Claude Code**: Optimized for speed using efficient LLM engines.
- 🛠️ **MCP Support**: Easily extend capabilities with Model Context Protocol.
- 📚 **SKILL.md System**: Modular skill system for specialized knowledge.
- 💻 **Interactive CLI**: Beautiful terminal interface with Rich and Prompt Toolkit.
- 🆓 **Free AI APIs**: Designed to work with free or low-cost OpenAI-compatible APIs.

## Installation
```bash
git clone https://github.com/yk445kauod-coder/manus-cli-agent.git
cd manus-cli-agent
pip install -r requirements.txt
```

## Usage
Set your API key:
```bash
export OPENAI_API_KEY="your_api_key"
```

Run the agent:
```bash
python src/main.py
```

## Project Structure
- `src/core`: LLM engine and core logic.
- `src/mcp`: Model Context Protocol manager.
- `src/skills`: SKILL.md management and skill definitions.
- `src/tools`: Built-in tools (shell, file, search).

## License
Open Source - MIT License
