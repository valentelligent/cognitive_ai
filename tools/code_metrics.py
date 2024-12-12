"""Code metrics collector for project documentation."""
import os
import ast
import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
import radon.raw as raw
import radon.metrics as metrics
from radon.complexity import cc_visit

def collect_file_metrics(file_path: str) -> Dict:
    """Collect metrics for a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic metrics
    basic_metrics = raw.analyze(content)
    
    # Cyclomatic complexity
    try:
        complexity = [node for node in cc_visit(content)]
        avg_complexity = sum(node.complexity for node in complexity) / len(complexity) if complexity else 0
    except:
        avg_complexity = 0
    
    # Maintainability Index
    try:
        mi_score = metrics.mi_visit(content, True)
    except:
        mi_score = 0
    
    return {
        "loc": basic_metrics.loc,
        "sloc": basic_metrics.sloc,
        "comments": basic_metrics.comments,
        "multi": basic_metrics.multi,
        "blank": basic_metrics.blank,
        "avg_complexity": round(avg_complexity, 2),
        "maintainability_index": round(mi_score, 2) if mi_score else 0
    }

def collect_project_metrics(project_root: str) -> Dict:
    """Collect metrics for the entire project."""
    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "files": {},
        "total": {
            "files": 0,
            "loc": 0,
            "sloc": 0,
            "comments": 0,
            "blank": 0,
            "avg_complexity": 0,
            "maintainability_index": 0
        }
    }
    
    total_files = 0
    total_complexity = 0
    total_mi = 0
    
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                
                try:
                    file_metrics = collect_file_metrics(file_path)
                    metrics_data["files"][rel_path] = file_metrics
                    
                    # Update totals
                    total_files += 1
                    metrics_data["total"]["loc"] += file_metrics["loc"]
                    metrics_data["total"]["sloc"] += file_metrics["sloc"]
                    metrics_data["total"]["comments"] += file_metrics["comments"]
                    metrics_data["total"]["blank"] += file_metrics["blank"]
                    total_complexity += file_metrics["avg_complexity"]
                    total_mi += file_metrics["maintainability_index"]
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    if total_files > 0:
        metrics_data["total"]["files"] = total_files
        metrics_data["total"]["avg_complexity"] = round(total_complexity / total_files, 2)
        metrics_data["total"]["maintainability_index"] = round(total_mi / total_files, 2)
    
    return metrics_data

def generate_metrics_rst(project_root: str, output_file: str):
    """Generate RST documentation with code metrics."""
    metrics = collect_project_metrics(project_root)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Code Metrics\n")
        f.write("===========\n\n")
        f.write(f"Last Updated: {datetime.fromisoformat(metrics['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Project totals
        f.write("Project Overview\n")
        f.write("-----------------\n\n")
        f.write(f"* Total Python Files: {metrics['total']['files']}\n")
        f.write(f"* Total Lines of Code: {metrics['total']['loc']}\n")
        f.write(f"* Total Source Lines of Code: {metrics['total']['sloc']}\n")
        f.write(f"* Total Comment Lines: {metrics['total']['comments']}\n")
        f.write(f"* Total Blank Lines: {metrics['total']['blank']}\n")
        f.write(f"* Average Cyclomatic Complexity: {metrics['total']['avg_complexity']}\n")
        f.write(f"* Average Maintainability Index: {metrics['total']['maintainability_index']}\n\n")
        
        # Individual file metrics
        f.write("File Metrics\n")
        f.write("------------\n\n")
        
        for file_path, file_metrics in sorted(metrics["files"].items()):
            f.write(f"**{file_path}**\n\n")
            f.write(f"* Lines of Code: {file_metrics['loc']}\n")
            f.write(f"* Source Lines of Code: {file_metrics['sloc']}\n")
            f.write(f"* Comment Lines: {file_metrics['comments']}\n")
            f.write(f"* Blank Lines: {file_metrics['blank']}\n")
            f.write(f"* Average Complexity: {file_metrics['avg_complexity']}\n")
            f.write(f"* Maintainability Index: {file_metrics['maintainability_index']}\n\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "docs", "code_metrics.rst")
    generate_metrics_rst(project_root, output_file)
