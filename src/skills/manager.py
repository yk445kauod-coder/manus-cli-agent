import os
import yaml
from typing import List, Dict, Any

class SkillManager:
    """
    مدير المهارات (Skills).
    يقوم بمسح المجلدات بحثاً عن ملفات SKILL.md وتحميلها.
    """
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills = {}
        self.load_skills()

    def load_skills(self):
        """
        تحميل جميع المهارات من المجلد المحدد.
        """
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return

        for skill_folder in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_folder)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, "SKILL.md")
                if os.path.exists(skill_file):
                    self.skills[skill_folder] = self._parse_skill(skill_file)

    def _parse_skill(self, file_path: str) -> Dict[str, Any]:
        """
        تحليل ملف SKILL.md لاستخراج البيانات الوصفية والمحتوى.
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # استخراج YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return {
                    "metadata": metadata,
                    "body": body,
                    "path": os.path.dirname(file_path)
                }
        
        return {"metadata": {"name": os.path.basename(os.path.dirname(file_path))}, "body": content, "path": os.path.dirname(file_path)}

    def get_skills_context(self) -> str:
        """
        تجميع أوصاف المهارات لإضافتها إلى سياق النظام.
        """
        context = "Available Skills:\n"
        for name, data in self.skills.items():
            desc = data["metadata"].get("description", "No description provided.")
            context += f"- {name}: {desc}\n"
        return context

    def get_skill_details(self, skill_name: str) -> str:
        """
        الحصول على تفاصيل مهارة معينة عند الحاجة.
        """
        if skill_name in self.skills:
            skill = self.skills[skill_name]
            return f"Skill: {skill['metadata']['name']}\n\n{skill['body']}"
        return "Skill not found."
