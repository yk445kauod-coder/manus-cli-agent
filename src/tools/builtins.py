import os
import requests

class BuiltinTools:
    @staticmethod
    def read_file(path: str):
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(path: str, content: str):
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"File written successfully to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @staticmethod
    def list_files(path: str = "."):
        try:
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @staticmethod
    def web_search(query: str):
        # محاكاة للبحث (يمكن ربطه بـ DuckDuckGo API مجاني)
        return f"Searching for: {query}... (Search results would appear here)"
