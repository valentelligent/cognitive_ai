"""Detailed metrics analyzer for component-level analysis."""
import os
import ast
import json
import time
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from radon.complexity import cc_rank
from radon.metrics import h_visit, mi_visit
import radon.raw as raw

@dataclass
class ComponentMetrics:
    name: str
    loc: int
    sloc: int
    comments: int
    complexity: float
    maintainability: float
    halstead: Dict
    dependencies: List[str]
    error_handlers: int
    memory_ops: int
    async_ops: int
    gpu_ops: int

def analyze_component(file_path: str) -> ComponentMetrics:
    """Analyze a single component for detailed metrics."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        tree = ast.parse(content)
    
    # Basic metrics
    raw_metrics = raw.analyze(content)
    
    # Complexity and maintainability
    complexity = sum(node.complexity for node in cc_visit(content))
    maintainability = mi_visit(content, multi=True)
    
    # Halstead metrics
    halstead = h_visit(content)
    
    # Custom metrics
    error_handlers = len([node for node in ast.walk(tree) 
                         if isinstance(node, ast.Try)])
    
    memory_ops = len([node for node in ast.walk(tree)
                     if isinstance(node, ast.Name) and 
                     any(mem in node.id.lower() for mem in ['memory', 'buffer', 'cache'])])
    
    async_ops = len([node for node in ast.walk(tree)
                    if isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith))])
    
    gpu_ops = len([node for node in ast.walk(tree)
                  if isinstance(node, ast.Name) and 
                  any(gpu in node.id.lower() for gpu in ['gpu', 'cuda', 'nvml'])])
    
    # Dependencies
    dependencies = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencies.extend(n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.append(node.module)
    
    return ComponentMetrics(
        name=Path(file_path).name,
        loc=raw_metrics.loc,
        sloc=raw_metrics.sloc,
        comments=raw_metrics.comments,
        complexity=complexity,
        maintainability=maintainability,
        halstead=halstead.__dict__ if halstead else {},
        dependencies=list(set(dependencies)),
        error_handlers=error_handlers,
        memory_ops=memory_ops,
        async_ops=async_ops,
        gpu_ops=gpu_ops
    )

def analyze_performance_bottlenecks(metrics: List[ComponentMetrics]) -> Dict:
    """Analyze potential performance bottlenecks."""
    bottlenecks = {
        "high_complexity": [],
        "memory_intensive": [],
        "gpu_intensive": [],
        "low_maintainability": []
    }
    
    for metric in metrics:
        if metric.complexity > 20:
            bottlenecks["high_complexity"].append({
                "file": metric.name,
                "complexity": metric.complexity
            })
        
        if metric.memory_ops > 5:
            bottlenecks["memory_intensive"].append({
                "file": metric.name,
                "memory_ops": metric.memory_ops
            })
        
        if metric.gpu_ops > 5:
            bottlenecks["gpu_intensive"].append({
                "file": metric.name,
                "gpu_ops": metric.gpu_ops
            })
        
        if metric.maintainability < 65:
            bottlenecks["low_maintainability"].append({
                "file": metric.name,
                "maintainability": metric.maintainability
            })
    
    return bottlenecks

def generate_optimization_recommendations(metrics: List[ComponentMetrics], 
                                       bottlenecks: Dict) -> List[Dict]:
    """Generate optimization recommendations based on metrics."""
    recommendations = []
    
    # Complexity recommendations
    for comp in bottlenecks["high_complexity"]:
        recommendations.append({
            "component": comp["file"],
            "issue": "High Complexity",
            "recommendation": "Consider breaking down complex functions into smaller, more manageable units",
            "priority": "High" if comp["complexity"] > 30 else "Medium"
        })
    
    # Memory optimization recommendations
    for mem in bottlenecks["memory_intensive"]:
        recommendations.append({
            "component": mem["file"],
            "issue": "Memory Usage",
            "recommendation": "Implement memory pooling or streaming for large operations",
            "priority": "High" if mem["memory_ops"] > 10 else "Medium"
        })
    
    # GPU optimization recommendations
    for gpu in bottlenecks["gpu_intensive"]:
        recommendations.append({
            "component": gpu["file"],
            "issue": "GPU Operations",
            "recommendation": "Batch GPU operations and implement memory management",
            "priority": "High" if gpu["gpu_ops"] > 10 else "Medium"
        })
    
    return recommendations

def generate_metrics_report(project_root: str) -> None:
    """Generate a comprehensive metrics report."""
    metrics = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    metric = analyze_component(file_path)
                    metrics.append(metric)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {str(e)}")
    
    bottlenecks = analyze_performance_bottlenecks(metrics)
    recommendations = generate_optimization_recommendations(metrics, bottlenecks)
    
    # Generate report
    report_path = os.path.join(project_root, "docs", "detailed_metrics.rst")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Detailed Component Metrics\n")
        f.write("========================\n\n")
        
        f.write("Component Analysis\n")
        f.write("-----------------\n\n")
        for metric in metrics:
            f.write(f"**{metric.name}**\n\n")
            f.write(f"* Lines of Code: {metric.loc}\n")
            f.write(f"* Source Lines: {metric.sloc}\n")
            f.write(f"* Comments: {metric.comments}\n")
            f.write(f"* Complexity: {metric.complexity}\n")
            f.write(f"* Maintainability: {metric.maintainability:.2f}\n")
            f.write(f"* Error Handlers: {metric.error_handlers}\n")
            f.write(f"* Memory Operations: {metric.memory_ops}\n")
            f.write(f"* GPU Operations: {metric.gpu_ops}\n")
            f.write(f"* Dependencies: {', '.join(metric.dependencies)}\n\n")
        
        f.write("Performance Bottlenecks\n")
        f.write("----------------------\n\n")
        for category, items in bottlenecks.items():
            if items:
                f.write(f"**{category.replace('_', ' ').title()}**\n\n")
                for item in items:
                    f.write(f"* {item['file']}: {list(item.values())[1]}\n")
                f.write("\n")
        
        f.write("Optimization Recommendations\n")
        f.write("--------------------------\n\n")
        for rec in recommendations:
            f.write(f"**{rec['component']}** ({rec['priority']})\n\n")
            f.write(f"* Issue: {rec['issue']}\n")
            f.write(f"* Recommendation: {rec['recommendation']}\n\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generate_metrics_report(project_root)
