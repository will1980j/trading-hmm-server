#!/usr/bin/env python3
"""
ACCURATE FULL VALIDATION - Filters false positives
"""
import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

def validate_html_template(template_path, template_name):
    """Validate HTML template"""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {template_name}")
    print(f"{'='*60}")
    
    errors = []
    
    if not os.path.exists(template_path):
        errors.append(f"Template not found: {template_path}")
        return False, errors
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ File loaded ({len(content):,} chars)")
    
    # 1) Check container tags
    print("\n1) Checking container tags...")
    self_closing = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
    
    open_tags = re.findall(r'<(\w+)[^>]*>', content)
    close_tags = re.findall(r'</(\w+)>', content)
    
    open_tags = [t for t in open_tags if t not in self_closing]
    
    from collections import Counter
    open_count = Counter(open_tags)
    close_count = Counter(close_tags)
    
    tag_errors = []
    for tag in set(open_count.keys()) | set(close_count.keys()):
        if open_count[tag] != close_count[tag]:
            tag_errors.append(f"Tag <{tag}>: {open_count[tag]} open, {close_count[tag]} close")
    
    if tag_errors:
        errors.extend(tag_errors)
        for err in tag_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ All container tags balanced")
    
    # 2) Check Jinja syntax
    print("\n2) Checking Jinja syntax...")
    
    jinja_errors = []
    
    # Check delimiters
    if content.count('{{') != content.count('}}'):
        jinja_errors.append(f"Unmatched {{ }}: {{ = {content.count('{{')}, }} = {content.count('}}')}") 
    
    if content.count('{%') != content.count('%}'):
        jinja_errors.append(f"Unmatched {{% %}}: {{% = {content.count('{%')}, %}} = {content.count('%}')}")
    
    # Check block structure (more accurate)
    lines = content.split('\n')
    block_stack = []
    for i, line in enumerate(lines, 1):
        # Find block starts
        if_match = re.search(r'\{%\s*if\s+', line)
        for_match = re.search(r'\{%\s*for\s+', line)
        block_match = re.search(r'\{%\s*block\s+', line)
        
        if if_match:
            block_stack.append(('if', i))
        if for_match:
            block_stack.append(('for', i))
        if block_match:
            block_stack.append(('block', i))
        
        # Find block ends
        endif_match = re.search(r'\{%\s*endif\s*%\}', line)
        endfor_match = re.search(r'\{%\s*endfor\s*%\}', line)
        endblock_match = re.search(r'\{%\s*endblock\s*%\}', line)
        
        if endif_match:
            if not block_stack or block_stack[-1][0] != 'if':
                jinja_errors.append(f"Line {i}: endif without matching if")
            else:
                block_stack.pop()
        
        if endfor_match:
            if not block_stack or block_stack[-1][0] != 'for':
                jinja_errors.append(f"Line {i}: endfor without matching for")
            else:
                block_stack.pop()
        
        if endblock_match:
            if not block_stack or block_stack[-1][0] != 'block':
                jinja_errors.append(f"Line {i}: endblock without matching block")
            else:
                block_stack.pop()
    
    if block_stack:
        for block_type, line_num in block_stack:
            jinja_errors.append(f"Line {line_num}: Unclosed {block_type} block")
    
    if jinja_errors:
        errors.extend(jinja_errors)
        for err in jinja_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ No Jinja errors")
    
    # 3) Test rendering
    print("\n3) Testing Jinja2 rendering...")
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(os.path.basename(template_path))
        context = {
            'current_user': {'username': 'test', 'is_authenticated': True},
            'request': {'endpoint': 'test'},
            'url_for': lambda x, **k: f"/{x}",
            'get_flashed_messages': lambda: [],
        }
        rendered = template.render(**context)
        print(f"  ✓ Renders successfully ({len(rendered):,} chars)")
    except Exception as e:
        error_msg = f"Rendering error: {str(e)}"
        errors.append(error_msg)
        print(f"  ✗ {error_msg}")
    
    return len(errors) == 0, errors

def validate_javascript(js_path, js_name, html_path):
    """Validate JavaScript"""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {js_name}")
    print(f"{'='*60}")
    
    errors = []
    
    if not os.path.exists(js_path):
        errors.append(f"JavaScript not found: {js_path}")
        return False, errors
    
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    print(f"✓ File loaded ({len(js_content):,} chars)")
    
    # 1) Syntax errors
    print("\n1) Checking syntax...")
    
    syntax_errors = []
    
    if js_content.count('{') != js_content.count('}'):
        syntax_errors.append(f"Unmatched braces: {{ = {js_content.count('{')}, }} = {js_content.count('}')}")
    else:
        print("  ✓ Braces balanced")
    
    if js_content.count('(') != js_content.count(')'):
        syntax_errors.append(f"Unmatched parentheses: ( = {js_content.count('(')}, ) = {js_content.count(')')}")
    else:
        print("  ✓ Parentheses balanced")
    
    if js_content.count('[') != js_content.count(']'):
        syntax_errors.append(f"Unmatched brackets: [ = {js_content.count('[')}, ] = {js_content.count(']')}")
    else:
        print("  ✓ Brackets balanced")
    
    if syntax_errors:
        errors.extend(syntax_errors)
        for err in syntax_errors:
            print(f"  ✗ {err}")
    
    # 2) Function duplicates
    print("\n2) Checking functions...")
    
    # Find function definitions
    func_pattern = r'function\s+(\w+)\s*\('
    const_func_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>)'
    
    functions = re.findall(func_pattern, js_content) + re.findall(const_func_pattern, js_content)
    
    from collections import Counter
    func_counts = Counter(functions)
    duplicates = [f for f, count in func_counts.items() if count > 1]
    
    if duplicates:
        for dup in duplicates:
            error_msg = f"Duplicate function: {dup} ({func_counts[dup]}x)"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
    else:
        print(f"  ✓ No duplicates ({len(functions)} functions)")
    
    # 3) DOM references (filter color codes)
    print("\n3) Checking DOM references...")
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Find JS ID references (excluding color codes)
        get_by_id = re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)', js_content)
        query_id = re.findall(r'querySelector\([\'"]#([^\'"]+)[\'"]\)', js_content)
        
        # Filter out color codes (hex colors)
        all_js_ids = set()
        for id_val in get_by_id + query_id:
            # Skip if it looks like a color code
            if not re.match(r'^[0-9a-fA-F]{6}$', id_val) and not re.match(r'^[0-9a-fA-F]{3}$', id_val):
                all_js_ids.add(id_val)
        
        # Find HTML IDs
        html_ids = set(re.findall(r'id=[\'"]([^\'"]+)[\'"]', html_content))
        
        # Check for missing
        missing_ids = all_js_ids - html_ids
        
        if missing_ids:
            for missing_id in sorted(missing_ids):
                error_msg = f"DOM element not found: #{missing_id}"
                errors.append(error_msg)
                print(f"  ✗ {error_msg}")
        else:
            print(f"  ✓ All DOM refs valid ({len(all_js_ids)} checked)")
    else:
        print("  ⚠ HTML not found - skipping DOM check")
    
    return len(errors) == 0, errors

def render_test(template_path, route_name):
    """Test rendering"""
    print(f"\n{'='*60}")
    print(f"RENDER TEST: {route_name}")
    print(f"{'='*60}")
    
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(os.path.basename(template_path))
        
        context = {
            'current_user': {'username': 'test', 'is_authenticated': True},
            'request': {'endpoint': 'test'},
            'url_for': lambda x, **k: f"/{x}",
            'get_flashed_messages': lambda: [],
        }
        
        rendered = template.render(**context)
        print(f"✓ Rendered: {len(rendered):,} chars")
        
        # Check for errors in output
        if any(err in rendered for err in ['Undefined', 'TypeError', 'Exception']):
            print("✗ Error indicators in output")
            return False
        
        print("✓ No error indicators")
        return True
        
    except Exception as e:
        print(f"✗ Render failed: {str(e)}")
        return False

def main():
    """Main validation"""
    print("="*60)
    print("FULL SYNTAX AND INTEGRATION VALIDATION")
    print("="*60)
    
    tests = [
        ('Homepage', '/homepage', 'templates/homepage_video_background.html', 'static/js/homepage.js'),
        ('Main Dashboard', '/main-dashboard', 'templates/main_dashboard.html', 'static/js/main_dashboard.js'),
        ('Automated Signals', '/automated-signals', 'templates/automated_signals_ultra.html', 'static/js/automated_signals_ultra.js'),
    ]
    
    all_passed = True
    all_errors = []
    
    for name, route, template, js in tests:
        html_ok, html_errs = validate_html_template(template, f"{name} Template")
        if not html_ok:
            all_passed = False
            all_errors.extend([f"{name} Template: {e}" for e in html_errs])
        
        js_ok, js_errs = validate_javascript(js, f"{name} JavaScript", template)
        if not js_ok:
            all_passed = False
            all_errors.extend([f"{name} JS: {e}" for e in js_errs])
        
        render_ok = render_test(template, route)
        if not render_ok:
            all_passed = False
            all_errors.append(f"{name}: Render failed")
    
    print(f"\n{'='*60}")
    print("FINAL RESULT")
    print(f"{'='*60}\n")
    
    if all_passed:
        print("🟢 ALL SYSTEMS GREEN 🟢\n")
        return 0
    else:
        print("🔴 VALIDATION FAILED 🔴\n")
        print("EXACT ERROR LINES:")
        for i, err in enumerate(all_errors, 1):
            print(f"{i}. {err}")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
