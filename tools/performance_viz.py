"""Performance visualization tool for identifying bottlenecks."""
import os
import json
from typing import Dict, List
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pathlib import Path

def create_performance_graph(metrics_data: Dict) -> None:
    """Create a performance dependency graph."""
    G = nx.DiGraph()
    
    # Node colors based on complexity
    colors = []
    sizes = []
    labels = {}
    
    for component in metrics_data:
        G.add_node(component.name)
        
        # Color based on complexity (red = high, green = low)
        complexity_color = min(component.complexity / 30, 1.0)
        colors.append((complexity_color, 0.5 - complexity_color/2, 0))
        
        # Size based on memory operations
        sizes.append(1000 + (component.memory_ops + component.gpu_ops) * 100)
        
        # Label with key metrics
        labels[component.name] = f"{component.name}\nC:{component.complexity:.1f}\nM:{component.maintainability:.1f}"
        
        # Add edges based on dependencies
        for dep in component.dependencies:
            if dep in [c.name for c in metrics_data]:
                G.add_edge(component.name, dep)
    
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Draw the graph
    nx.draw(G, pos, 
           node_color=colors,
           node_size=sizes,
           labels=labels,
           font_size=8,
           font_weight='bold',
           edge_color='gray',
           arrows=True,
           arrowsize=20)
    
    plt.title("Component Performance Graph\nNode Size: Memory/GPU Usage, Color: Complexity")
    plt.savefig(os.path.join("docs", "_static", "performance_graph.png"), 
                format='png', dpi=300, bbox_inches='tight')
    plt.close()

def create_bottleneck_heatmap(metrics_data: Dict) -> None:
    """Create a heatmap of performance bottlenecks."""
    components = [m.name for m in metrics_data]
    metrics = ['complexity', 'memory_ops', 'gpu_ops', 'maintainability']
    
    data = np.zeros((len(components), len(metrics)))
    for i, component in enumerate(metrics_data):
        data[i] = [
            component.complexity / 30,  # Normalize complexity
            component.memory_ops / 10,  # Normalize memory ops
            component.gpu_ops / 10,    # Normalize GPU ops
            (100 - component.maintainability) / 100  # Invert maintainability
        ]
    
    plt.figure(figsize=(12, 8))
    plt.imshow(data, cmap='YlOrRd', aspect='auto')
    
    # Add labels
    plt.xticks(range(len(metrics)), metrics, rotation=45)
    plt.yticks(range(len(components)), components)
    
    # Add colorbar
    plt.colorbar(label='Normalized Impact')
    
    plt.title("Performance Bottleneck Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join("docs", "_static", "bottleneck_heatmap.png"), 
                format='png', dpi=300, bbox_inches='tight')
    plt.close()

def create_optimization_priority_chart(recommendations: List[Dict]) -> None:
    """Create a chart showing optimization priorities."""
    components = []
    priorities = []
    issues = []
    
    for rec in recommendations:
        components.append(rec['component'])
        priorities.append(2 if rec['priority'] == 'High' else 1)
        issues.append(rec['issue'])
    
    plt.figure(figsize=(12, 6))
    
    # Create horizontal bar chart
    y_pos = np.arange(len(components))
    plt.barh(y_pos, priorities, 
            color=['red' if p == 2 else 'orange' for p in priorities])
    
    # Customize the chart
    plt.yticks(y_pos, components)
    plt.xlabel('Priority Level')
    plt.title('Optimization Priority Chart')
    
    # Add issue labels
    for i, v in enumerate(priorities):
        plt.text(v, i, f' {issues[i]}', va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join("docs", "_static", "optimization_priorities.png"), 
                format='png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_performance_report(metrics_data: Dict, recommendations: List[Dict]) -> None:
    """Generate a comprehensive performance report with visualizations."""
    # Create visualizations
    create_performance_graph(metrics_data)
    create_bottleneck_heatmap(metrics_data)
    create_optimization_priority_chart(recommendations)
    
    # Generate report
    report_path = os.path.join("docs", "performance_analysis.rst")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Performance Analysis\n")
        f.write("===================\n\n")
        
        f.write("Component Performance Graph\n")
        f.write("-------------------------\n\n")
        f.write(".. image:: _static/performance_graph.png\n")
        f.write("   :alt: Component Performance Graph\n")
        f.write("   :align: center\n\n")
        f.write("This graph shows component relationships and performance characteristics:\n\n")
        f.write("* Node size indicates memory and GPU operation intensity\n")
        f.write("* Node color indicates complexity (red = high, green = low)\n")
        f.write("* Edges show dependencies between components\n\n")
        
        f.write("Bottleneck Analysis\n")
        f.write("------------------\n\n")
        f.write(".. image:: _static/bottleneck_heatmap.png\n")
        f.write("   :alt: Bottleneck Heatmap\n")
        f.write("   :align: center\n\n")
        f.write("The heatmap shows normalized impact of different performance factors:\n\n")
        f.write("* Complexity: Cyclomatic complexity of the component\n")
        f.write("* Memory Ops: Intensity of memory operations\n")
        f.write("* GPU Ops: Intensity of GPU operations\n")
        f.write("* Maintainability: Inverse of maintainability index\n\n")
        
        f.write("Optimization Priorities\n")
        f.write("---------------------\n\n")
        f.write(".. image:: _static/optimization_priorities.png\n")
        f.write("   :alt: Optimization Priorities\n")
        f.write("   :align: center\n\n")
        f.write("Priority levels for recommended optimizations:\n\n")
        f.write("* High (Red): Critical improvements needed\n")
        f.write("* Medium (Orange): Important but not critical\n\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # First run detailed metrics
    from detailed_metrics import generate_metrics_report
    generate_metrics_report(project_root)
    
    # Then generate performance visualizations
    generate_performance_report(metrics_data, recommendations)
