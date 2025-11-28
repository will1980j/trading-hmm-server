#!/usr/bin/env python3
"""
Comprehensive Template Validation Script
Tests homepage, main-dashboard, and automated-signals for all errors
"""
import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, UndefinedError
from jinja2.exceptions import TemplateError

def setup_jinja_env():
    """Setup Jinja2 environment"""
    if not os.path.exists('templates'):
        print("❌ templates/ directory not found")
        return None
    
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=True
    )
    return env

def create_mock_context():
    """Create comprehensive mock context"""
    return {
        'current_user': {'username': 'test_user', 'is_authenticated': True},
        'request': {'endpoint': 'test'},
        'url_for': lambda endpoint, **kwargs: f"/{endpoint}",
        'get_flashed_messages': lambda: [],
        'config': {'SECRET_KEY': 'test'},
        # Homepage specific
        'homepage_stats': {
            'total_signals': 42,
            'win_rate': 75.5,
            'avg_mfe': 2.3,
            'active_trades': 5,
            'best_session': 'ASIA',
            'best_session_mfe': 4.14
        },
        'roadmap_progress': {
            'current_phase': 'H1.4',
            'completion_percentage': 85,
            'phases': []
        },
        # Main dashboard specific
        'dashboard_stats': {
            'signals_today': 12,
            'active_count': 3,
            'win_rate': 80.0,
            'avg_mfe': 2.1
        },
        # Automated signals specific
        'signals_stats': {
            'total_signals': 15,
            'active_count': 2,
            'completed_count': 13,
            'win_rate': 85.0,
            'avg_mfe': 1.9
        }
    }

def validate_template(env, template_name, display_name, context):
    """Validate a single template"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTING: {display_name}")
    print(f"{'='*60}")
    
    errors = []
    warnings = []
    
    try:
        # Load template
        print(f"  📄 Loading template: {template_name}")
        template = env.get_template(template_name)
        print(f"  ✅ Template loaded successfully")
        
        # Render template
        print(f"  🎨 Rendering template...")
        rendered = template.render(**context)
        print(f"  ✅ Template rendered successfully ({len(rendered):,} chars)")
        
        # Validate rendered content
        if not rendered.strip():
            warnings.append("Template rendered empty content")
        
        # Check for unrendered Jinja
        jinja_patterns = ['{{', '}}', '{%', '%}', '{#', '#}']
        for pattern in jinja_patterns:
            if pattern in rendered:
                count = rendered.count(pattern)
                warnings.append(f"Found {count} unrendered Jinja pattern: {pattern}")
        
        # Check HTML structure
        if '<html' in rendered.lower() and '</html>' in rendered.lower():
            print(f"  ✅ Valid HTML structure detected")
        else:
            warnings.append("No complete HTML structure found")
        
        # Check for common error indicators
        error_indicators = [
            'Undefined',
            'UndefinedError',
            'TemplateSyntaxError',
            'TypeError',
            'AttributeError'
        ]
        for indicator in error_indicators:
            if indicator in rendered:
                errors.append(f"Found error indicator in output: {indicator}")
        
        # Report results
        if errors:
            print(f"\n  ❌ ERRORS FOUND:")
            for error in errors:
                print(f"     • {error}")
        
        if warnings:
            print(f"\n  ⚠️  WARNINGS:")
            for warning in warnings:
                print(f"     • {warning}")
        
        if not errors and not warnings:
            print(f"\n  ✅ ALL CHECKS PASSED - Template is valid!")
        
        return len(errors) == 0, errors, warnings
        
    except TemplateSyntaxError as e:
        error_msg = f"Template Syntax Error on line {e.lineno}: {e.message}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        return False, errors, warnings
        
    except UndefinedError as e:
        error_msg = f"Undefined Variable Error: {e}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        return False, errors, warnings
        
    except TemplateError as e:
        error_msg = f"Template Error: {e}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        return False, errors, warnings
        
    except Exception as e:
        error_msg = f"Unexpected Error: {e}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        return False, errors, warnings

def validate_javascript(js_file, display_name):
    """Validate JavaScript file"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTING: {display_name} JavaScript")
    print(f"{'='*60}")
    
    if not os.path.exists(js_file):
        print(f"  ❌ File not found: {js_file}")
        return False, [f"File not found: {js_file}"], []
    
    errors = []
    warnings = []
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"  📄 File loaded: {len(content):,} chars")
        
        # Check for balanced braces
        brace_count = content.count('{') - content.count('}')
        if brace_count != 0:
            errors.append(f"Unmatched braces: {brace_count}")
        else:
            print(f"  ✅ Braces balanced")
        
        # Check for balanced parentheses
        paren_count = content.count('(') - content.count(')')
        if paren_count != 0:
            errors.append(f"Unmatched parentheses: {paren_count}")
        else:
            print(f"  ✅ Parentheses balanced")
        
        # Check for balanced brackets
        bracket_count = content.count('[') - content.count(']')
        if bracket_count != 0:
            errors.append(f"Unmatched brackets: {bracket_count}")
        else:
            print(f"  ✅ Brackets balanced")
        
        # Check for common syntax errors
        if 'function(' in content:
            print(f"  ✅ Functions detected")
        
        if 'console.log' in content:
            warnings.append("Contains console.log statements (consider removing for production)")
        
        # Report results
        if errors:
            print(f"\n  ❌ ERRORS FOUND:")
            for error in errors:
                print(f"     • {error}")
        
        if warnings:
            print(f"\n  ⚠️  WARNINGS:")
            for warning in warnings:
                print(f"     • {warning}")
        
        if not errors and not warnings:
            print(f"\n  ✅ ALL CHECKS PASSED - JavaScript is valid!")
        
        return len(errors) == 0, errors, warnings
        
    except Exception as e:
        error_msg = f"Error reading file: {e}"
        print(f"  ❌ {error_msg}")
        return False, [error_msg], []

def main():
    """Main validation function"""
    print("🚀 COMPREHENSIVE TEMPLATE VALIDATION")
    print("="*60)
    
    # Setup Jinja environment
    env = setup_jinja_env()
    if not env:
        return 1
    
    # Create mock context
    context = create_mock_context()
    
    # Templates to test
    templates_to_test = [
        ('homepage_video_background.html', 'Homepage', 'static/js/homepage.js'),
        ('main_dashboard.html', 'Main Dashboard', 'static/js/main_dashboard.js'),
        ('automated_signals_ultra.html', 'Automated Signals', 'static/js/automated_signals_ultra.js')
    ]
    
    results = {}
    
    # Test each template
    for template_file, display_name, js_file in templates_to_test:
        # Test template
        template_path = f"templates/{template_file}"
        if os.path.exists(template_path):
            success, errors, warnings = validate_template(env, template_file, display_name, context)
            results[f"{display_name} Template"] = {
                'success': success,
                'errors': errors,
                'warnings': warnings
            }
        else:
            print(f"\n{'='*60}")
            print(f"🔍 TESTING: {display_name}")
            print(f"{'='*60}")
            print(f"  ❌ Template file not found: {template_path}")
            results[f"{display_name} Template"] = {
                'success': False,
                'errors': [f"Template file not found: {template_path}"],
                'warnings': []
            }
        
        # Test JavaScript
        success, errors, warnings = validate_javascript(js_file, display_name)
        results[f"{display_name} JavaScript"] = {
            'success': success,
            'errors': errors,
            'warnings': warnings
        }
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"\n{status} {name}")
        
        if result['errors']:
            print(f"  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    • {error}")
        
        if result['warnings']:
            print(f"  Warnings: {len(result['warnings'])}")
            for warning in result['warnings']:
                print(f"    • {warning}")
        
        if not result['success']:
            all_passed = False
    
    # Overall result
    print(f"\n{'='*60}")
    print(f"🎯 OVERALL RESULT")
    print(f"{'='*60}")
    
    if all_passed:
        print(f"✅ ALL TESTS PASSED - Ready for deployment!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED - Review issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
