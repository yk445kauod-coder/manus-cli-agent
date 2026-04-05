import os
import sys
import json
import subprocess
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# إضافة المسار الحالي لـ sys.path لتمكين الاستيراد
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm import LLMEngine
from src.mcp.manager import MCPManager
from src.skills.manager import SkillManager
from src.config import Config
from src.tools.builtins import BuiltinTools

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class WebAgent:
    def __init__(self):
        self.llm = LLMEngine()
        self.mcp = MCPManager()
        self.skills = SkillManager(Config.SKILLS_DIR)
        self.history = []
        self._setup_system_prompt()
        self._register_default_tools()

    def _setup_system_prompt(self):
        skills_context = self.skills.get_skills_context()
        self.system_prompt = f"""
        You are Manus Web Agent, a fast and powerful AI assistant developed by {Config.DEVELOPER}.
        You are designed to be faster than Claude Code and support MCP and SKILL.md systems.
        You are currently running in a Web Interface.
        
        {skills_context}
        
        When you need to use a skill, mention it. When you need to use a tool, call it via MCP.
        Always be concise, professional, and helpful.
        """
        self.history.append({"role": "system", "content": self.system_prompt})

    def _register_default_tools(self):
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
        self.mcp.register_tool(name="read_file", description="Read content from a file.", parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, handler=BuiltinTools.read_file)
        self.mcp.register_tool(name="write_file", description="Write content to a file.", parameters={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}, handler=BuiltinTools.write_file)
        self.mcp.register_tool(name="list_files", description="List files in a directory.", parameters={"type": "object", "properties": {"path": {"type": "string", "default": "."}}}, handler=BuiltinTools.list_files)
        self.mcp.register_tool(name="web_search", description="Search the web for information.", parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}, handler=BuiltinTools.web_search)

    def _execute_shell(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def process_query(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        
        # إرسال حالة "Thinking" للواجهة
        socketio.emit('status', {'message': 'Thinking...'})
        
        response = self.llm.chat(self.history, tools=self.mcp.get_tool_specs())
        
        if not response:
            socketio.emit('error', {'message': 'Failed to get response from LLM.'})
            return

        message = response.choices[0].message
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                socketio.emit('status', {'message': f'Executing Tool: {tool_name}...'})
                result = self.mcp.call_tool(tool_name, tool_args)
                
                self.history.append(message)
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result
                })
                
                # متابعة المعالجة بعد تنفيذ الأداة
                return self.process_query("Continue based on tool result.")

        content = message.content
        if content:
            self.history.append({"role": "assistant", "content": content})
            socketio.emit('response', {'content': content})

agent = WebAgent()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_input')
def handle_user_input(data):
    user_input = data.get('message')
    if user_input:
        agent.process_query(user_input)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
