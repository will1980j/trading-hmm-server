import os
import re

def find_database_url_occurrences(root_dir="."):
    """Find all DATABASE_URL occurrences with context"""
    results = []
    
    # Skip these directories
    skip_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.kiro', 'backups'}
    
    for root, dirs, files in os.walk(root_dir):
        # Remove skip directories from dirs list
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if not file.endswith(('.py', '.md', '.txt', '.env', '.json', '.toml')):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    if 'DATABASE_URL' in line:
                        # Get 10 lines before and after
                        start = max(0, i - 10)
                        end = min(len(lines), i + 11)
                        context = lines[start:end]
                        
                        results.append({
                            'file': filepath,
                            'line_num': i + 1,
                            'line': line.strip(),
                            'context': ''.join(context)
                        })
            except Exception as e:
                pass
    
    return results

if __name__ == "__main__":
    results = find_database_url_occurrences()
    
    for r in results:
        print("=" * 80)
        print(f"FILE: {r['file']}")
        print(f"LINE {r['line_num']}: {r['line']}")
        print("-" * 80)
        print(r['context'])
        print()
