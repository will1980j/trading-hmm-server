#!/usr/bin/env python3
"""
Export Amazon Q prompts for use in other IDEs
"""

import os
import json
from pathlib import Path

def find_q_prompts():
    """Find Amazon Q prompts directory"""
    q_paths = [
        Path.home() / ".aws" / "amazonq" / "prompts",
        Path.home() / "AppData" / "Roaming" / "amazonq" / "prompts",
        Path("C:") / "Users" / os.getenv("USERNAME", "") / ".aws" / "amazonq" / "prompts"
    ]
    
    for path in q_paths:
        if path.exists():
            return path
    return None

def export_prompts():
    """Export Q prompts to a readable format"""
    prompts_dir = find_q_prompts()
    if not prompts_dir:
        print("No Amazon Q prompts found")
        return
    
    print(f"Found Q prompts in: {prompts_dir}")
    
    exported = {}
    prompt_files = list(prompts_dir.glob("*.json"))
    
    if not prompt_files:
        print("No prompt files found")
        return
    
    for prompt_file in prompt_files:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                prompt_name = prompt_file.stem
                exported[prompt_name] = {
                    "content": data.get("content", ""),
                    "description": data.get("description", "")
                }
        except Exception as e:
            print(f"Error reading {prompt_file}: {e}")
    
    # Save to project directory
    output_file = "q_prompts_export.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)
    
    print(f"\nExported {len(exported)} prompts to {output_file}")
    
    # Also create a readable markdown file
    md_file = "q_prompts_export.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Amazon Q Prompts Export\n\n")
        for name, data in exported.items():
            f.write(f"## {name}\n\n")
            if data.get("description"):
                f.write(f"**Description:** {data['description']}\n\n")
            f.write(f"```\n{data['content']}\n```\n\n")
    
    print(f"Also created readable version: {md_file}")
    
    return exported

def create_windsurf_guide():
    """Create guide for using prompts in Windsurf"""
    guide = """# Using Q Prompts in Windsurf

## Method 1: Copy-Paste Prompts
1. Open `q_prompts_export.md`
2. Copy the prompt content you need
3. Paste into Windsurf chat
4. Add your specific context/files

## Method 2: Create Windsurf Rules
1. Create `.windsurf/rules.md` in your project
2. Add your most-used prompts as rules
3. Windsurf will automatically apply them

## Method 3: Manual Prompt Library
Keep `q_prompts_export.json` handy and reference prompts as needed.

## Key Differences:
- **Amazon Q**: Uses @file, @workspace syntax
- **Windsurf**: Uses file selection or drag-and-drop
- **Amazon Q**: Saved prompts with @prompt
- **Windsurf**: Manual copy-paste or rules

## Recommendation:
Use VS Code + Amazon Q on your personal machine for identical experience.
"""
    
    with open("windsurf_prompts_guide.md", 'w') as f:
        f.write(guide)
    
    print("Created windsurf_prompts_guide.md")

def main():
    print("Amazon Q Prompts Exporter\n")
    exported = export_prompts()
    if exported:
        create_windsurf_guide()
        print("\nFiles created:")
        print("- q_prompts_export.json (machine readable)")
        print("- q_prompts_export.md (human readable)")
        print("- windsurf_prompts_guide.md (usage guide)")

if __name__ == "__main__":
    main()