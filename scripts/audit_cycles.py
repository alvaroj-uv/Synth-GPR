
import os
import ast
import sys
from collections import defaultdict

def find_files(src_dir):
    py_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def resolve_module(file_path, import_node, src_root):
    """Resolve an import string to a standardized module name."""
    try:
        rel_path = os.path.relpath(file_path, os.path.dirname(src_root))
    except ValueError:
        return None
        
    current_pkg = rel_path.replace(os.sep, ".").replace(".py", "")
    if current_pkg.endswith(".__init__"):
        current_pkg = current_pkg[:-9]
    
    current_parts = current_pkg.split(".")[:-1] # Package parts
    
    target = None
    
    if isinstance(import_node, ast.Import):
        # absolute imports
        for alias in import_node.names:
            if alias.name.startswith("src."): 
                target = alias.name
    elif isinstance(import_node, ast.ImportFrom):
        if import_node.level > 0:
            # Relative import
            if len(current_parts) < import_node.level - 1:
                return None 
            
            base_parts = current_parts[:len(current_parts) - (import_node.level - 1)]
            if import_node.module:
                target = ".".join(base_parts + [import_node.module])
        else:
             # Absolute from
             if import_node.module and import_node.module.startswith("src"):
                 target = import_node.module
    
    return target

def build_graph(src_dir):
    graph = defaultdict(set)
    files = find_files(src_dir)
    src_root = src_dir
    
    # Map file paths to module names
    path_to_mod = {}
    for p in files:
        try:
            rel = os.path.relpath(p, os.path.dirname(src_dir))
            mod = rel.replace(os.sep, ".").replace(".py", "")
            if mod.endswith(".__init__"):
                mod = mod[:-9]
            path_to_mod[p] = mod
        except ValueError:
            continue
        
    known_modules = set(path_to_mod.values())

    for p in files:
        current_mod = path_to_mod.get(p)
        if not current_mod: continue
        
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                tree = ast.parse(f.read())
            except:
                continue
                
        for node in ast.walk(tree):
            target = resolve_module(p, node, src_dir)
            if target:
                if target in known_modules and target != current_mod:
                    graph[current_mod].add(target)

    return graph

def find_cycles(graph):
    cycles = []
    
    def visit(node, path, visited):
        if node in path:
            cycle = path[path.index(node):] + [node]
            cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            visit(neighbor, path, visited)
            
        path.pop()

    visited = set()
    for node in list(graph.keys()):
        if node not in visited:
             visit(node, [], visited)
             
    return cycles

if __name__ == "__main__":
    # Hardcoded to check ../src relative to this script location (scripts/audit_cycles.py)
    # This avoids arg parsing issues and ensures we check the right target
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.abspath(os.path.join(script_dir, "../src"))
        
    print(f"Checking for cycles in {src_dir}...")
    
    if not os.path.exists(src_dir):
        print(f"Error: Directory {src_dir} does not exist.")
        sys.exit(1)
    
    graph = build_graph(src_dir)
    print(f"Built dependency graph with {len(graph)} modules.")
    
    cycles = find_cycles(graph)
    if cycles:
        print(f"FOUND {len(cycles)} CYCLES:")
        for c in cycles:
            print(" -> ".join(c))
        sys.exit(1)
    else:
        print("No circular dependencies found.")
        sys.exit(0)
