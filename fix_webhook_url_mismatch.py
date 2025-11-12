"""
Fix webhook URL mismatch by adding route alias
"""

def add_webhook_alias():
    """Add /webhook route alias to web_server.py"""
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the automated_signals_webhook function
    webhook_function_line = "@app.route('/api/automated-signals', methods=['POST'])"
    
    if webhook_function_line in content:
        # Add alias route right after the main route
        alias_code = """
@app.route('/api/automated-signals/webhook', methods=['POST'])
def automated_signals_webhook_alias():
    \"\"\"Alias for backward compatibility with /webhook suffix\"\"\"
    return automated_signals_webhook()

"""
        
        # Insert alias after the main route definition
        insertion_point = content.find(webhook_function_line)
        if insertion_point != -1:
            # Find the end of the function definition line
            next_line = content.find('\n', insertion_point)
            # Find the start of the next function
            next_def = content.find('\ndef ', next_line)
            
            # Insert alias before the function body
            content = content[:next_line + 1] + alias_code + content[next_line + 1:]
            
            with open('web_server.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ Added /webhook route alias to web_server.py")
            print("\nBoth URLs now work:")
            print("  - /api/automated-signals")
            print("  - /api/automated-signals/webhook")
            print("\nDeploy to Railway to activate the fix.")
            return True
    
    print("❌ Could not find webhook function in web_server.py")
    return False

if __name__ == "__main__":
    add_webhook_alias()
