#!/usr/bin/env python3
"""
PHASE 2: Comprehensive Feature Gating System
Applies feature flags to web_server.py and prop_firm_registry.py
Based on findings from COMPREHENSIVE_SQL_TABLE_ANALYSIS_PHASE1.md
"""

import os
import re

# Feature flag configuration to add at top of web_server.py
FEATURE_FLAGS = '''
# ============================================================================
# FEATURE FLAGS - Control optional modules and legacy systems
# ============================================================================
# Set via environment variables (default: false for all optional features)
ENABLE_LEGACY = os.environ.get("ENABLE_LEGACY", "false").lower() == "true"
ENABLE_PREDICTION = os.environ.get("ENABLE_PREDICTION", "false").lower() == "true"
ENABLE_PROP = os.environ.get("ENABLE_PROP", "false").lower() == "true"
ENABLE_V2 = os.environ.get("ENABLE_V2", "false").lower() == "true"
ENABLE_REPLAY = os.environ.get("ENABLE_REPLAY", "false").lower() == "true"
ENABLE_EXECUTION = os.environ.get("ENABLE_EXECUTION", "false").lower() == "true"
ENABLE_TELEMETRY_LEGACY = os.environ.get("ENABLE_TELEMETRY_LEGACY", "false").lower() == "true"

# H1 CORE is ALWAYS enabled (automated_signals table and related functionality)
# These flags control OPTIONAL features only
# ============================================================================
'''

def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write file content"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def backup_file(filepath):
    """Create backup of file"""
    backup_path = f"{filepath}.backup_phase2"
    content = read_file(filepath)
    write_file(backup_path, content)
    print(f"✅ Backed up {filepath} to {backup_path}")

def patch_web_server():
    """Apply comprehensive gating to web_server.py"""
    print("\n🔧 PATCHING web_server.py...")
    
    filepath = "web_server.py"
    backup_file(filepath)
    
    content = read_file(filepath)
    
    # Step 1: Add feature flags after imports
    # Find the line with "from execution_router import ExecutionRouter"
