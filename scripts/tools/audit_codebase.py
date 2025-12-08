import os
import ast
from pathlib import Path
import datetime

# Configuration
ROOT_DIR = r"d:\Codigo\Synth-GPR"
LEGACY_DIR = r"d:\Codigo\Synth-GPR\legacy"
SKIP_DIRS = {'.git', '__pycache__', 'legacy', 'venv', 'env', '.ipynb_checkpoints'}
# Files known to be critical entry points even if not imported
WHITELIST_CORE = {
    'generate_balanced_dataset.py',
    'create_feature_dataset.py',
    'setup_tests.bat', # Not python but critical
    'test_pipeline.bat',
    'validate_tests.bat'
}

def get_python_files(root):
    py_files = []
    for root_path, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.py'):
                py_files.append(Path(root_path) / f)
    return py_files

def get_imports(file_path):
    """Parse a file and return a set of module names it imports."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
            elif node.level > 0:
                # Relative import (e.g. from . import config)
                # This is tricky to resolve exactly to a file without more context,
                # but we know it imports *something* local.
                # For this audit, we care if a file IS imported.
                pass
    return imports

def analyze_codebase():
    all_files = get_python_files(ROOT_DIR)
    file_map = {f.name: f for f in all_files} # valid approximation for unique filenames usually
    
    # Build usage graph
    # Key: potentially imported module name
    # Value: list of files that import it
    usage_counts = {f.stem: 0 for f in all_files}
    
    # Also track explicit string references (e.g. subprocess calls)
    
    entry_points = []
    
    print(f"Scanning {len(all_files)} files...")
    
    for f_path in all_files:
        # Check if it has a main block
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'if __name__' in content and '__main__' in content:
                    entry_points.append(f_path.name)
        except:
            pass
            
        # Imports logic (Simplified for "is imported")
        # If file A imports 'src.config', then 'config.py' in src is used.
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    # simplistic matching: if import 'src.workers', then workers.py is used
                    parts = node.module.split('.')
                    for part in parts:
                        if part in usage_counts:
                            usage_counts[part] += 1
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        parts = alias.name.split('.')
                        for part in parts:
                             if part in usage_counts:
                                usage_counts[part] += 1
        except Exception:
            pass

    # Categorize
    active_core = []
    standalone_tools = []
    candidates = []

    for f_path in all_files:
        name = f_path.name
        stem = f_path.stem
        
        is_whitelisted = name in WHITELIST_CORE
        is_imported = usage_counts.get(stem, 0) > 0
        has_main = name in entry_points
        is_test = name.startswith('test_') or name.startswith('verify_')
        is_tool = 'scripts' in str(f_path) or 'visualization' in str(f_path)
        
        if is_whitelisted or is_imported:
            active_core.append(f_path)
        elif is_test:
             standalone_tools.append(f_path) # Tests are valid tools
        elif has_main or is_tool:
            standalone_tools.append(f_path)
        else:
            candidates.append(f_path)
            
    # Generate Report
    report_lines = ["# Code Audit Report\n"]
    report_lines.append(f"Generated on: {datetime.datetime.now()}\n")
    
    report_lines.append("\n## Summary")
    report_lines.append(f"- Total Files: {len(all_files)}")
    report_lines.append(f"- Active Core: {len(active_core)}")
    report_lines.append(f"- Standalone/Tools: {len(standalone_tools)}")
    report_lines.append(f"- **Candidates for Legacy**: {len(candidates)}\n")
    
    report_lines.append("## Active Core")
    for f in active_core:
        report_lines.append(f"- {f.relative_to(ROOT_DIR)}")
        
    report_lines.append("\n## Standalone / Tools / Tests")
    for f in standalone_tools:
        report_lines.append(f"- {f.relative_to(ROOT_DIR)}")
        
    report_lines.append("\n## Candidates for Legacy (To Move)")
    for f in candidates:
        report_lines.append(f"- {f.relative_to(ROOT_DIR)}")
        
    with open("CODE_AUDIT_REPORT.md", "w", encoding='utf-8') as f:
        f.writelines([l + '\n' for l in report_lines])
        
    print("Audit Complete. See CODE_AUDIT_REPORT.md")

if __name__ == "__main__":
    analyze_codebase()
