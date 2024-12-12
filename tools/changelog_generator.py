"""
Automatic changelog generator for Cognitive AI project.
Tracks file changes, updates, and modifications across the project.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path
import re

class ChangelogGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.changes_file = self.project_root / "docs" / "changes.json"
        self.load_changes()

    def load_changes(self) -> None:
        """Load existing changes from JSON file."""
        if self.changes_file.exists():
            with open(self.changes_file, 'r') as f:
                self.changes = json.load(f)
        else:
            self.changes = {
                "last_update": "",
                "versions": [],
                "components": {}
            }

    def save_changes(self) -> None:
        """Save changes to JSON file."""
        self.changes["last_update"] = datetime.now().isoformat()
        with open(self.changes_file, 'w') as f:
            json.dump(self.changes, f, indent=2)

    def scan_project(self) -> Dict:
        """Scan project for changes and updates."""
        components = {
            "core": self._scan_directory(self.project_root / "core"),
            "tests": self._scan_directory(self.project_root / "tests"),
            "docs": self._scan_directory(self.project_root / "docs"),
            "config": self._scan_config_files(),
        }
        return components

    def _scan_directory(self, directory: Path) -> Dict:
        """Scan a directory for Python files and their contents."""
        if not directory.exists():
            return {}

        components = {}
        for file in directory.rglob("*.py"):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                components[file.relative_to(self.project_root).as_posix()] = {
                    "classes": self._extract_classes(content),
                    "functions": self._extract_functions(content),
                    "last_modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                }
        return components

    def _scan_config_files(self) -> Dict:
        """Scan configuration files."""
        config_files = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "environment.yml",
            ".pre-commit-config.yaml"
        ]
        
        configs = {}
        for file in config_files:
            path = self.project_root / file
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    configs[file] = {
                        "content": f.read(),
                        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                    }
        return configs

    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python content."""
        return [m.group(1) for m in re.finditer(r"class\s+(\w+)\s*[:\(]", content)]

    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from Python content."""
        return [m.group(1) for m in re.finditer(r"def\s+(\w+)\s*\(", content)]

    def generate_rst(self) -> str:
        """Generate RST documentation from changes."""
        components = self.scan_project()
        
        rst = ["Project Status and Changes\n========================\n\n"]
        rst.append(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Core Components
        rst.append("Core Components\n---------------\n\n")
        if "core" in components:
            for file, details in components["core"].items():
                rst.append(f"**{file}**\n\n")
                if details["classes"]:
                    rst.append("Classes:\n")
                    for cls in details["classes"]:
                        rst.append(f"* ``{cls}``\n")
                if details["functions"]:
                    rst.append("\nFunctions:\n")
                    for func in details["functions"]:
                        rst.append(f"* ``{func}``\n")
                rst.append(f"\nLast Modified: {details['last_modified']}\n\n")

        # Tests
        rst.append("Test Suite\n----------\n\n")
        if "tests" in components:
            for file, details in components["tests"].items():
                rst.append(f"**{file}**\n\n")
                if details["classes"]:
                    rst.append("Test Classes:\n")
                    for cls in details["classes"]:
                        rst.append(f"* ``{cls}``\n")
                rst.append(f"\nLast Modified: {details['last_modified']}\n\n")

        # Configuration
        rst.append("Configuration\n-------------\n\n")
        if "config" in components:
            for file, details in components["config"].items():
                rst.append(f"**{file}**\n")
                rst.append(f"Last Modified: {details['last_modified']}\n\n")

        return "".join(rst)

    def update_documentation(self) -> None:
        """Update project documentation with changes."""
        rst_content = self.generate_rst()
        status_file = self.project_root / "docs" / "project_status.rst"
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(rst_content)
        self.save_changes()

def main():
    """Main function to generate changelog."""
    if len(sys.argv) != 2:
        print("Usage: python changelog_generator.py <project_root>")
        sys.exit(1)

    generator = ChangelogGenerator(sys.argv[1])
    generator.update_documentation()
    print("Documentation updated successfully!")

if __name__ == "__main__":
    main()
