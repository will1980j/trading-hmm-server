#!/usr/bin/env python3
"""
FULL SYNTAX AND INTEGRATION VALIDATION
Comprehensive validation for all three pages
"""
import os
import sys
import re
from html.parser import HTMLParser
from jinja2 import Environment, FileSystemLoader

class HTMLValidator(HTMLParser):
    """Validate HTML structure"""
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.line_num = 1
        
    def handle_starttag(self, tag, attrs):
        if tag not in ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr']:
            self.stack.append((tag, self.line_num))
    
    def handle_endtag(self, tag):
        if tag not in ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr']:
            if not self.stack:
                self.errors.append(f"Line {self.line_num}: Closing tag </{tag}> without opening tag")
            else:
                last_tag, last_line = self.stack.pop()
                if last_tag != tag:
                    self.errors.append(f"Line {self.line_num}: Mismatched tags - expected </{last_tag}> (opened at line {last_line}), got </{tag}>")
    
    def handle_data(self, data):
        self.line_num += data.count('\n')

def validate_html_template(template_path, template_name):
    """Validate HTML template structure"""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {template_name}")
    print(f"{'='*60}")
    
    errors = []
    
    if not os.path.exists(template_path):
        errors.append(f"Template file not found: {template_path}")
        return False, errors
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ File loaded ({len(content):,} chars)")
        
        # Check for missing tags
        print("\n1) Checking for missing/mismatched tags...")
        
        # Basic tag balance check
        open_tags = re.findall(r'<(\w+)[^>]*>', content)
        close_tags = re.findall(r'</(\w+)>', content)
        
        # Filter out self-closing tags
        self_closing = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
        open_tags = [t for t in open_tags if t not in self_closing]
        
        # Count occurrences
        from collections import Counter
        open_count = Counter(open_tags)
        close_count = Counter(close_tags)
        
        # Check for mismatches
        all_tags = set(open_count.keys()) | set(close_count.keys())
        tag_errors = []
        for tag in all_tags:
            if open_count[tag] != close_count[tag]:
                tag_errors.append(f"  ✗ Tag <{tag}>: {open_count[tag]} opening, {close_count[tag]} closing")
        
        if tag_errors:
            errors.extend(tag_errors)
            for err in tag_errors:
                print(err)
        else:
            print("  ✓ All container tags balanced")
        
        # Check for Jinja errors
        print("\n2) Checking for Jinja errors...")
        
        jinja_errors = []
        
        # Check for unmatched Jinja delimiters
        jinja_open = content.count('{{')
        jinja_close = content.count('}}')
        if jinja_open != jinja_close:
            jinja_errors.append(f"  ✗ Unmatched Jinja expressions: {{ = {jinja_open}, }} = {jinja_close}")
        
        block_open = content.count('{%')
        block_close = content.count('%}')
        if block_open != block_close:
            jinja_errors.append(f"  ✗ Unmatched Jinja blocks: {{% = {block_open}, %}} = {block_close}")
        
        # Check for common Jinja syntax errors
        if re.search(r'\{\{[^}]*\{[^}]*\}\}', content):
            jinja_errors.append("  ✗ Nested Jinja expressions detected")
        
        # Check for unclosed Jinja blocks
        block_pattern = r'\{%\s*(\w+)\s+.*?%\}'
        blocks = re.findall(block_pattern, content)
        block_stack = []
        for match in re.finditer(block_pattern, content):
            block_type = match.group(1)
            if block_type in ['if', 'for', 'block', 'macro']:
                block_stack.append(block_type)
            elif block_type in ['endif', 'endfor', 'endblock', 'endmacro']:
                expected = block_type.replace('end', '')
                if not block_stack or block_stack[-1] != expected:
                    jinja_errors.append(f"  ✗ Mismatched Jinja block: {block_type}")
                elif block_stack:
                    block_stack.pop()
        
        if block_stack:
            jinja_errors.append(f"  ✗ Unclosed Jinja blocks: {', '.join(block_stack)}")
        
        if jinja_errors:
            errors.extend(jinja_errors)
            for err in jinja_errors:
                print(err)
        else:
            print("  ✓ No Jinja errors detected")
        
        # Try to render with Jinja2
        print("\n3) Testing Jinja2 rendering...")
        try:
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template(os.path.basename(template_path))
            
            # Mock context
            context = {
                'current_user': {'username': 'test', 'is_authenticated': True},
                'request': {'endpoint': 'test'},
                'url_for': lambda x, **k: f"/{x}",
                'get_flashed_messages': lambda: [],
            }
            
            rendered = template.render(**context)
            print(f"  ✓ Template renders successfully ({len(rendered):,} chars)")
            
        except Exception as e:
            error_msg = f"  ✗ Jinja2 rendering error: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        error_msg = f"Error reading template: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {error_msg}")
        return False, errors

def validate_javascript(js_path, js_name, html_path):
    """Validate JavaScript file"""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {js_name}")
    print(f"{'='*60}")
    
    errors = []
    
    if not os.path.exists(js_path):
        errors.append(f"JavaScript file not found: {js_path}")
        return False, errors
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        print(f"✓ File loaded ({len(js_content):,} chars)")
        
        # 1) Check syntax errors
        print("\n1) Checking for syntax errors...")
        
        syntax_errors = []
        
        # Check balanced braces
        brace_count = js_content.count('{') - js_content.count('}')
        if brace_count != 0:
            syntax_errors.append(f"  ✗ Unmatched braces: {brace_count} ({{ = {js_content.count('{')}, }} = {js_content.count('}')})")
        else:
            print("  ✓ Braces balanced")
        
        # Check balanced parentheses
        paren_count = js_content.count('(') - js_content.count(')')
        if paren_count != 0:
            syntax_errors.append(f"  ✗ Unmatched parentheses: {paren_count} (( = {js_content.count('(')}, ) = {js_content.count(')')})")
        else:
            print("  ✓ Parentheses balanced")
        
        # Check balanced brackets
        bracket_count = js_content.count('[') - js_content.count(']')
        if bracket_count != 0:
            syntax_errors.append(f"  ✗ Unmatched brackets: {bracket_count} ([ = {js_content.count('[')}, ] = {js_content.count(']')})")
        else:
            print("  ✓ Brackets balanced")
        
        if syntax_errors:
            errors.extend(syntax_errors)
            for err in syntax_errors:
                print(err)
        
        # 2) Check for missing or duplicated functions
        print("\n2) Checking for missing/duplicated functions...")
        
        # Find all function definitions
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>))'
        functions = re.findall(function_pattern, js_content)
        function_names = [f[0] or f[1] for f in functions]
        
        # Check for duplicates
        from collections import Counter
        func_counts = Counter(function_names)
        duplicates = [f for f, count in func_counts.items() if count > 1]
        
        if duplicates:
            for dup in duplicates:
                error_msg = f"  ✗ Duplicate function: {dup} (defined {func_counts[dup]} times)"
                errors.append(error_msg)
                print(error_msg)
        else:
            print(f"  ✓ No duplicate functions ({len(function_names)} unique functions)")
        
        # 3) Check references to nonexistent DOM elements
        print("\n3) Checking DOM element references...")
        
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Find all getElementById calls
            get_by_id = re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)', js_content)
            # Find all querySelector with IDs
            query_id = re.findall(r'querySelector\([\'"]#([^\'"]+)[\'"]\)', js_content)
            # Find all direct ID references
            direct_id = re.findall(r'[\'"]#([a-zA-Z][\w-]+)[\'"]', js_content)
            
            all_js_ids = set(get_by_id + query_id + direct_id)
            
            # Find all IDs in HTML
            html_ids = set(re.findall(r'id=[\'"]([^\'"]+)[\'"]', html_content))
            
            # Check for missing IDs
            missing_ids = all_js_ids - html_ids
            
            if missing_ids:
                for missing_id in sorted(missing_ids):
                    error_msg = f"  ✗ DOM element not found in HTML: #{missing_id}"
                    errors.append(error_msg)
                    print(error_msg)
            else:
                print(f"  ✓ All DOM references valid ({len(all_js_ids)} IDs checked)")
        else:
            print("  ⚠ HTML file not found - skipping DOM validation")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        error_msg = f"Error reading JavaScript: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {error_msg}")
        return False, errors

def render_test(template_path, route_name):
    """Test template rendering"""
    print(f"\n{'='*60}")
    print(f"RENDER TEST: {route_name}")
    print(f"{'='*60}")
    
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(os.path.basename(template_path))
        
        # Comprehensive mock context
        context = {
            'current_user': {'username': 'test_user', 'is_authenticated': True},
            'request': {'endpoint': 'test'},
            'url_for': lambda x, **k: f"/{x}",
            'get_flashed_messages': lambda: [],
            'config': {},
            'homepage_stats': {'total_signals': 42, 'win_rate': 75.5, 'avg_mfe': 2.3},
            'roadmap_progress': {'current_phase': 'H1.4', 'completion_percentage': 85},
            'dashboard_stats': {'signals_today': 12, 'active_count': 3},
            'signals_stats': {'total_signals': 15, 'active_count': 2},
        }
        
        rendered = template.render(**context)
        print(f"✓ Render successful: {len(rendered):,} chars")
        
        # Check for error indicators
        error_indicators = ['Undefined', 'Error', 'Exception', 'TypeError']
        found_errors = [ind for ind in error_indicators if ind in rendered]
        
        if found_errors:
            print(f"✗ Error indicators found in output: {', '.join(found_errors)}")
            return False
        
        print("✓ No error indicators in rendered output")
        return True
        
    except Exception as e:
        print(f"✗ Render failed: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("="*60)
    print("FULL SYNTAX AND INTEGRATION VALIDATION")
    print("="*60)
    
    # Test configurations
    tests = [
        {
            'name': 'Homepage',
            'route': '/homepage',
            'template': 'templates/homepage_video_background.html',
            'js': 'static/js/homepage.js'
        },
        {
            'name': 'Main Dashboard',
            'route': '/main-dashboard',
            'template': 'templates/main_dashboard.html',
            'js': 'static/js/main_dashboard.js'
        },
        {
            'name': 'Automated Signals',
            'route': '/automated-signals',
            'template': 'templates/automated_signals_ultra.html',
            'js': 'static/js/automated_signals_ultra.js'
        }
    ]
    
    all_passed = True
    all_errors = []
    
    # Run validations
    for test in tests:
        # Validate HTML template
        html_passed, html_errors = validate_html_template(test['template'], f"{test['name']} Template")
        if not html_passed:
            all_passed = False
            all_errors.extend([f"{test['name']} Template: {err}" for err in html_errors])
        
        # Validate JavaScript
        js_passed, js_errors = validate_javascript(test['js'], f"{test['name']} JavaScript", test['template'])
        if not js_passed:
            all_passed = False
            all_errors.extend([f"{test['name']} JavaScript: {err}" for err in js_errors])
        
        # Render test
        render_passed = render_test(test['template'], test['route'])
        if not render_passed:
            all_passed = False
            all_errors.append(f"{test['name']}: Render test failed")
    
    # Final result
    print(f"\n{'='*60}")
    print("FINAL RESULT")
    print(f"{'='*60}")
    
    if all_passed:
        print("\n🟢 ALL SYSTEMS GREEN 🟢\n")
        return 0
    else:
        print("\n🔴 VALIDATION FAILED 🔴\n")
        print("EXACT ERROR LINES:")
        for i, error in enumerate(all_errors, 1):
            print(f"{i}. {error}")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
