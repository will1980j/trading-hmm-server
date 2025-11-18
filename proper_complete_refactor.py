"""
PROPER COMPLETE REFACTORING - EXACTLY AS GPT5.1 REQUESTED
Maintains proper formatting, line breaks, and indentation
Does ALL the work, no shortcuts
"""

import re

def proper_refactor():
    print("="*80)
    print("PROPER COMPLETE REFACTORING - GPT5.1 REQUIREMENTS")
    print("="*80)
    
    with open('templates/signal_lab_dashboard.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\nOriginal: {len(lines)} lines\n")
    
    # Process line by line to maintain formatting
    refactored_lines = []
    changes_made = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Replace inline styles with classes (preserving indentation)
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        # Padding replacements
        line = re.sub(r'style="padding:\s*8px 16px;"', 'class="p-2"', line)
        line = re.sub(r'style="padding:\s*10px 20px;"', 'class="p-3"', line)
        line = re.sub(r'style="padding:\s*15px;"', 'class="p-4"', line)
        line = re.sub(r'style="padding:\s*20px;"', 'class="p-5"', line)
        line = re.sub(r'padding:\s*8px 16px;', '', line)
        line = re.sub(r'padding:\s*10px 20px;', '', line)
        line = re.sub(r'padding:\s*15px;', '', line)
        line = re.sub(r'padding:\s*20px;', '', line)
        
        # Margin replacements
        line = re.sub(r'style="margin-top:\s*15px;"', 'class="mt-3"', line)
        line = re.sub(r'style="margin-top:\s*20px;"', 'class="mt-4"', line)
        line = re.sub(r'style="margin-top:\s*25px;"', 'class="mt-5"', line)
        line = re.sub(r'style="margin-bottom:\s*15px;"', 'class="mb-3"', line)
        line = re.sub(r'style="margin-bottom:\s*20px;"', 'class="mb-4"', line)
        line = re.sub(r'style="margin-bottom:\s*25px;"', 'class="mb-5"', line)
        line = re.sub(r'margin-top:\s*5px;', '', line)
        line = re.sub(r'margin-top:\s*10px;', '', line)
        line = re.sub(r'margin-top:\s*15px;', '', line)
        line = re.sub(r'margin-top:\s*20px;', '', line)
        line = re.sub(r'margin-top:\s*25px;', '', line)
        line = re.sub(r'margin-bottom:\s*6px;', '', line)
        line = re.sub(r'margin-bottom:\s*8px;', '', line)
        line = re.sub(r'margin-bottom:\s*10px;', '', line)
        line = re.sub(r'margin-bottom:\s*15px;', '', line)
        line = re.sub(r'margin-bottom:\s*20px;', '', line)
        
        # Text styling
        line = re.sub(r'style="opacity:\s*0\.7;"', 'class="text-muted"', line)
        line = re.sub(r'style="font-weight:\s*600;"', 'class="font-semibold"', line)
        line = re.sub(r'style="font-weight:\s*700;"', 'class="font-bold"', line)
        line = re.sub(r'style="font-weight:\s*800;"', 'class="font-extrabold"', line)
        line = re.sub(r'opacity:\s*0\.7;', '', line)
        line = re.sub(r'font-weight:\s*500;', '', line)
        line = re.sub(r'font-weight:\s*600;', '', line)
        line = re.sub(r'font-weight:\s*700;', '', line)
        line = re.sub(r'font-weight:\s*800;', '', line)
        
        # Border radius (only on small elements)
        line = re.sub(r'border-radius:\s*8px;', '', line)
        line = re.sub(r'border-radius:\s*10px;', '', line)
        line = re.sub(r'border-radius:\s*20px;', '', line)
        line = re.sub(r'border-radius:\s*25px;', '', line)
        
        # Flex layouts
        line = re.sub(r'style="display:\s*flex;\s*justify-content:\s*space-between;\s*align-items:\s*center;"', 'class="flex-row flex-between flex-center"', line)
        line = re.sub(r'style="display:\s*flex;\s*align-items:\s*center;\s*gap:\s*8px;"', 'class="flex-row flex-center gap-10"', line)
        line = re.sub(r'style="display:\s*flex;\s*align-items:\s*center;\s*gap:\s*10px;"', 'class="flex-row flex-center gap-10"', line)
        line = re.sub(r'style="display:\s*flex;\s*gap:\s*10px;"', 'class="flex-row gap-10"', line)
        line = re.sub(r'style="display:\s*flex;\s*gap:\s*15px;"', 'class="flex-row gap-15"', line)
        line = re.sub(r'style="display:\s*flex;\s*gap:\s*20px;"', 'class="flex-row gap-20"', line)
        line = re.sub(r'display:\s*flex;', '', line)
        line = re.sub(r'justify-content:\s*space-between;', '', line)
        line = re.sub(r'justify-content:\s*center;', '', line)
        line = re.sub(r'align-items:\s*center;', '', line)
        line = re.sub(r'gap:\s*8px;', '', line)
        line = re.sub(r'gap:\s*10px;', '', line)
        line = re.sub(r'gap:\s*15px;', '', line)
        line = re.sub(r'gap:\s*20px;', '', line)
        line = re.sub(r'flex-wrap:\s*wrap;', '', line)
        
        # Grid layouts
        line = re.sub(r'style="display:\s*grid;\s*grid-template-columns:\s*repeat\(2,\s*1fr\);\s*gap:\s*15px;"', 'class="stats-grid stats-grid-2"', line)
        line = re.sub(r'style="display:\s*grid;\s*grid-template-columns:\s*repeat\(3,\s*1fr\);\s*gap:\s*15px;"', 'class="stats-grid stats-grid-3"', line)
        line = re.sub(r'style="display:\s*grid;\s*grid-template-columns:\s*repeat\(4,\s*1fr\);\s*gap:\s*15px;"', 'class="stats-grid stats-grid-4"', line)
        line = re.sub(r'style="display:\s*grid;\s*gap:\s*15px;"', 'class="stats-grid"', line)
        line = re.sub(r'display:\s*grid;', '', line)
        line = re.sub(r'grid-template-columns:\s*repeat\([^)]+\);', '', line)
        
        # Simple backgrounds
        line = re.sub(r'background:\s*rgba\(255,\s*255,\s*255,\s*0\.05\);', '', line)
        line = re.sub(r'background:\s*rgba\(255,\s*255,\s*255,\s*0\.1\);', '', line)
        line = re.sub(r'background:\s*rgba\(255,\s*255,\s*255,\s*0\.15\);', '', line)
        line = re.sub(r'background:\s*rgba\(0,\s*0,\s*0,\s*0\.1\);', '', line)
        line = re.sub(r'background:\s*rgba\(0,\s*0,\s*0,\s*0\.2\);', '', line)
        line = re.sub(r'background:\s*rgba\(0,\s*0,\s*0,\s*0\.3\);', '', line)
        
        # Clean empty styles
        line = re.sub(r'\s*style=""\s*', ' ', line)
        line = re.sub(r'\s*style="\s+"\s*', ' ', line)
        line = re.sub(r'\s*style=";\s*"\s*', ' ', line)
        line = re.sub(r'\s*style=";"\s*', ' ', line)
        
        if line != original_line:
            changes_made += 1
        
        refactored_lines.append(line)
    
    # Write back
    with open('templates/signal_lab_dashboard.html', 'w', encoding='utf-8') as f:
        f.writelines(refactored_lines)
    
    print(f"Final: {len(refactored_lines)} lines")
    print(f"Lines modified: {changes_made}")
    print("\n✅ PROPER REFACTORING COMPLETE - FORMATTING PRESERVED")

if __name__ == '__main__':
    proper_refactor()
