#!/usr/bin/env python3

import requests

def deploy_v2_incremental():
    """Deploy V2 schema incrementally to identify issues"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 INCREMENTAL V2 DEPLOYMENT")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Read the V2 schema
    try:
        with open('database/signal_lab_v2_schema.sql', 'r') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("❌ Schema file not found!")
        return
    
    # Split into main sections
    sections = []
    current_section = ""
    section_name = "Initial"
    
    for line in schema_sql.split('\n'):
        if line.strip().startswith('-- ') and 'TABLE' in line.upper():
            if current_section.strip():
                sections.append((section_name, current_section.strip()))
            section_name = line.strip()
            current_section = ""
        current_section += line + "\n"
    
    if current_section.strip():
        sections.append((section_name, current_section.strip()))
    
    print(f"📋 Found {len(sections)} schema sections")
    
    # Deploy each section
    for i, (name, sql) in enumerate(sections):
        print(f"\n📝 Section {i+1}/{len(sections)}: {name}")
        print(f"   Size: {len(sql)} characters")
        
        # Skip empty sections
        if len(sql.strip()) < 10:
            print("   ⏭️ Skipping empty section")
            continue
        
        try:
            payload = {"schema_sql": sql}
            response = session.post(
                f"{base_url}/api/deploy-signal-lab-v2",
                json=payload,
                timeout=60
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                tables = result.get('tables_created', [])
                print(f"   ✅ Success: {len(tables)} tables created")
                if tables:
                    print(f"      Tables: {', '.join(tables)}")
            else:
                print(f"   ❌ Failed: {response.text}")
                # Continue with other sections
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🎯 DEPLOYMENT COMPLETE")
    print(f"Check Railway logs for any remaining issues")

if __name__ == "__main__":
    deploy_v2_incremental()