"""
Agent Skill Registry & Knowledge Retrieval Engine.
Allows procurement agents to dynamically discover, inspect, and read their own skills/theories.
"""
import os
from typing import Dict, List, Optional

_SKILLS_DIR = os.path.dirname(__file__)


class SkillRegistry:
    def __init__(self, skills_dir: str = _SKILLS_DIR):
        self.skills_dir = skills_dir

    def list_skills(self) -> List[str]:
        """Returns all available skill filenames (.md)."""
        return [f for f in os.listdir(self.skills_dir) if f.endswith(".md")]

    def read_skill(self, skill_name: str) -> Optional[str]:
        """Reads and returns the content of a specific skill markdown document."""
        if not skill_name.endswith(".md"):
            skill_name += ".md"
        path = os.path.join(self.skills_dir, skill_name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def get_skill_catalog(self) -> Dict[str, str]:
        """Returns brief titles of all available skills for agent dynamic discovery."""
        catalog = {}
        for s in self.list_skills():
            content = self.read_skill(s)
            title = content.splitlines()[0] if content else s
            catalog[s] = title.replace("# ", "").strip()
        return catalog


skill_registry = SkillRegistry()
