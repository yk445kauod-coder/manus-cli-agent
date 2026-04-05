import json
import os
from typing import List, Dict, Any

class MCPManager:
    """
    مدير بروتوكول سياق النموذج (MCP).
    يتيح هذا النظام تسجيل الأدوات واستدعاءها.
    """
    def __init__(self):
        self.tools = {}
        self.mcp_config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.mcp_config_path):
            with open(self.mcp_config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"servers": []}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler: callable):
        """
        تسجيل أداة جديدة في النظام.
        """
        self.tools[name] = {
            "spec": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            },
            "handler": handler
        }

    def get_tool_specs(self) -> List[Dict[str, Any]]:
        """
        الحصول على مواصفات الأدوات بتنسيق OpenAI.
        """
        return [tool["spec"] for tool in self.tools.values()]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        استدعاء أداة مسجلة.
        """
        if name in self.tools:
            try:
                result = self.tools[name]["handler"](**arguments)
                return str(result)
            except Exception as e:
                return f"Error executing tool {name}: {str(e)}"
        return f"Tool {name} not found."

    def add_mcp_server(self, server_url: str):
        """
        إضافة خادم MCP خارجي (مستقبلاً).
        """
        self.config["servers"].append(server_url)
        with open(self.mcp_config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
