import os
import sys
import json
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

# إضافة المسار الحالي لـ sys.path لتمكين الاستيراد
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm import LLMEngine
from src.mcp.manager import MCPManager
from src.skills.manager import SkillManager
from src.config import Config
from src.tools.builtins import BuiltinTools

console = Console()

class ManusCLI:
    def __init__(self):
        self.llm = LLMEngine()
        self.mcp = MCPManager()
        self.skills = SkillManager(Config.SKILLS_DIR)
        self.history = []
        self.session = PromptSession(
            history=FileHistory(os.path.expanduser("~/.manus_cli_history")),
            auto_suggest=AutoSuggestFromHistory(),
            style=Style.from_dict({
                'prompt': '#00ff00 bold',
            })
        )
        self._setup_system_prompt()
        self._register_default_tools()

    def _setup_system_prompt(self):
        skills_context = self.skills.get_skills_context()
        self.system_prompt = f"""
        You are Manus CLI Agent, a fast and powerful AI assistant developed by {Config.DEVELOPER}.
        You are designed to be faster than Claude Code and support MCP and SKILL.md systems.
        
        {skills_context}
        
        When you need to use a skill, mention it. When you need to use a tool, call it via MCP.
        Always be concise, professional, and helpful.
        """
        self.history.append({"role": "system", "content": self.system_prompt})

    def _register_default_tools(self):
        # تسجيل أدوات افتراضية
        self.mcp.register_tool(
            name="execute_shell",
            description="Execute a shell command in the sandbox.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run."}
                },
                "required": ["command"]
            },
            handler=self._execute_shell
        )
        
        self.mcp.register_tool(
            name="read_file",
            description="Read content from a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."}
                },
                "required": ["path"]
            },
            handler=BuiltinTools.read_file
        )
        
        self.mcp.register_tool(
            name="write_file",
            description="Write content to a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."},
                    "content": {"type": "string", "description": "Content to write."}
                },
                "required": ["path", "content"]
            },
            handler=BuiltinTools.write_file
        )
        
        self.mcp.register_tool(
            name="list_files",
            description="List files in a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory.", "default": "."}
                }
            },
            handler=BuiltinTools.list_files
        )
        
        self.mcp.register_tool(
            name="web_search",
            description="Search the web for information.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            },
            handler=BuiltinTools.web_search
        )

    def _execute_shell(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def run(self):
        console.print(Panel(
            f"[bold green]Manus CLI Agent[/bold green]\n"
            f"Developed by: [bold cyan]{Config.DEVELOPER}[/bold cyan]\n"
            f"Model: [yellow]{Config.MODEL}[/yellow]\n"
            f"Type 'exit' or 'quit' to stop.",
            title="Welcome",
            border_style="bright_blue"
        ))

        while True:
            try:
                user_input = self.session.prompt("manus-cli > ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue

                self.history.append({"role": "user", "content": user_input})
                self._process_query()

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def _process_query(self):
        with console.status("[bold green]Thinking...", spinner="dots"):
            response = self.llm.chat(self.history, tools=self.mcp.get_tool_specs())
            
        if not response:
            console.print("[red]Error: Failed to get response from LLM.[/red]")
            return

        message = response.choices[0].message
        
        # التعامل مع استدعاء الأدوات
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                console.print(f"[bold yellow]Executing Tool: {tool_name}...[/bold yellow]")
                result = self.mcp.call_tool(tool_name, tool_args)
                
                # إضافة نتيجة الأداة للتاريخ والمتابعة
                self.history.append(message)
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result
                })
                
                # طلب رد نهائي بعد تنفيذ الأداة
                self._process_query()
                return

        # عرض الرد النهائي
        content = message.content
        if content:
            self.history.append({"role": "assistant", "content": content})
            console.print(Markdown(content))

if __name__ == "__main__":
    agent = ManusCLI()
    agent.run()
