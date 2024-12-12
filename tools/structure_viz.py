"""Project structure visualizer for documentation."""
import os
import ast
from typing import Dict, List, Set
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

def analyze_imports(file_path: str) -> Set[str]:
    """Analyze Python file imports."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Error analyzing imports in {file_path}: {str(e)}")
    return imports

def generate_dependency_graph(project_root: str) -> nx.DiGraph:
    """Generate a dependency graph of Python modules."""
    G = nx.DiGraph()
    
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                module_name = os.path.splitext(rel_path)[0].replace(os.sep, '.')
                
                G.add_node(module_name)
                imports = analyze_imports(file_path)
                
                for imp in imports:
                    if imp != module_name:
                        G.add_edge(module_name, imp)
    
    return G

def generate_structure_viz(project_root: str, output_file: str):
    """Generate project structure visualization."""
    G = generate_dependency_graph(project_root)
    
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=8, font_weight='bold',
            arrows=True, edge_color='gray', arrowsize=20)
    
    plt.savefig(os.path.join(project_root, 'docs', '_static', 'dependency_graph.png'),
                format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate RST documentation
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Project Structure\n")
        f.write("================\n\n")
        
        f.write("Module Dependencies\n")
        f.write("-----------------\n\n")
        f.write(".. image:: _static/dependency_graph.png\n")
        f.write("   :alt: Project Dependency Graph\n")
        f.write("   :align: center\n\n")
        
        f.write("Directory Structure\n")
        f.write("------------------\n\n")
        f.write(".. code-block:: text\n\n")
        
        for root, dirs, files in os.walk(project_root):
            level = root.replace(project_root, '').count(os.sep)
            indent = '    ' * level
            f.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = '    ' * (level + 1)
            for file in sorted(files):
                if not file.startswith('.') and not file.startswith('__'):
                    f.write(f'{subindent}{file}\n')

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "docs", "project_structure.rst")
    generate_structure_viz(project_root, output_file)
