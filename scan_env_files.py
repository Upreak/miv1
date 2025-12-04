#!/usr/bin/env python3
"""
Comprehensive .env File Scanner

This script performs a complete scan of the project directory structure
to locate and catalog all .env files with detailed analysis.
"""

import os
import sys
import stat
import json
from pathlib import Path
from datetime import datetime

def scan_env_files(root_path="."):
    """Scan for all .env files in the project"""
    env_files = []
    root_path = Path(root_path).resolve()
    
    print(f"🔍 Starting comprehensive .env file scan from: {root_path}")
    print("=" * 80)
    
    # Walk through all directories
    for root, dirs, files in os.walk(root_path):
        # Skip common directories that shouldn't contain .env files
        dirs[:] = [d for d in dirs if d not in {
            '.git', '.vscode', '__pycache__', 'node_modules', 
            '.pytest_cache', '.mypy_cache', 'venv', 'env', 
            '.venv', 'build', 'dist', '.next', '.nuxt'
        }]
        
        for file in files:
            if file.startswith('.env'):
                file_path = Path(root) / file
                env_files.append(file_path)
    
    return env_files, root_path

def analyze_env_file(file_path, root_path):
    """Analyze a single .env file"""
    try:
        # Get file stats
        stat_info = file_path.stat()
        file_size = stat_info.st_size
        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
        
        # Get file permissions
        file_mode = stat_info.st_mode
        permissions = oct(file_mode)[-3:]
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Parse environment variables
        variables = {}
        sensitive_vars = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Parse variable assignment
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                variables[key] = {
                    'value': value,
                    'line': line_num,
                    'is_empty': not value,
                    'has_quotes': line.count('"') > 0 or line.count("'") > 0
                }
                
                # Check if sensitive
                if is_sensitive_variable(key, value):
                    sensitive_vars.append(key)
        
        # Categorize variables
        categories = categorize_variables(variables)
        
        return {
            'file_path': file_path,
            'relative_path': str(file_path.relative_to(root_path)),
            'absolute_path': str(file_path),
            'file_size': file_size,
            'modified_time': modified_time,
            'permissions': permissions,
            'total_variables': len(variables),
            'variables': variables,
            'sensitive_variables': sensitive_vars,
            'categories': categories,
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        }
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'error_type': type(e).__name__
        }

def is_sensitive_variable(key, value):
    """Check if a variable contains sensitive information"""
    key_lower = key.lower()
    sensitive_keywords = [
        'password', 'passwd', 'pwd', 'secret', 'key', 'token', 'auth',
        'api_key', 'apikey', 'credential', 'cert', 'private', 'public',
        'db_pass', 'database_password', 'smtp_pass', 'mail_pass',
        'jwt_secret', 'session_secret', 'encryption_key', 'hash_key'
    ]
    
    # Check key
    for keyword in sensitive_keywords:
        if keyword in key_lower:
            return True
    
    # Check value patterns
    if value:
        # API keys (common patterns)
        if any(pattern in value.lower() for pattern in ['sk-', 'pk-', 'ak-', 'secret-', 'token-']):
            return True
        
        # JWT tokens
        if '.' in value and len(value) > 20:
            parts = value.split('.')
            if len(parts) == 3:
                try:
                    # Basic JWT structure check
                    import base64
                    base64.b64decode(parts[0] + '==')
                    base64.b64decode(parts[1] + '==')
                    return True
                except:
                    pass
    
    return False

def categorize_variables(variables):
    """Categorize variables by type"""
    categories = {
        'API Keys': [],
        'Database Credentials': [],
        'Authentication': [],
        'Application Settings': [],
        'Security': [],
        'External Services': [],
        'Development': [],
        'Other': []
    }
    
    for key in variables.keys():
        key_lower = key.lower()
        
        if any(word in key_lower for word in ['api', 'key', 'token']):
            categories['API Keys'].append(key)
        elif any(word in key_lower for word in ['db', 'database', 'mysql', 'postgres', 'mongodb']):
            categories['Database Credentials'].append(key)
        elif any(word in key_lower for word in ['auth', 'login', 'user', 'pass']):
            categories['Authentication'].append(key)
        elif any(word in key_lower for word in ['app', 'debug', 'env', 'mode']):
            categories['Application Settings'].append(key)
        elif any(word in key_lower for word in ['ssl', 'tls', 'cert', 'encrypt']):
            categories['Security'].append(key)
        elif any(word in key_lower for word in ['smtp', 'mail', 'email', 'aws', 'gcp', 'azure']):
            categories['External Services'].append(key)
        elif any(word in key_lower for word in ['test', 'dev', 'local']):
            categories['Development'].append(key)
        else:
            categories['Other'].append(key)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def check_git_status(file_path):
    """Check if file is tracked by git"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'ls-files', str(file_path)],
            capture_output=True, text=True, cwd=file_path.parent
        )
        return result.returncode == 0 and result.stdout.strip()
    except:
        return None

def generate_report(env_files, root_path):
    """Generate comprehensive report"""
    print("\n📋 ENVIRONMENT FILE ANALYSIS REPORT")
    print("=" * 80)
    
    if not env_files:
        print("❌ No .env files found in the project")
        return
    
    print(f"✅ Found {len(env_files)} .env file(s)\n")
    
    total_vars = 0
    total_sensitive = 0
    security_issues = []
    
    for i, file_path in enumerate(env_files, 1):
        print(f"📄 File {i}: {file_path.name}")
        print(f"   📁 Path: {file_path}")
        print(f"   📏 Size: {file_path.stat().st_size} bytes")
        print(f"   ⏱️  Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
        
        # Analyze file
        analysis = analyze_env_file(file_path, root_path)
        
        if 'error' in analysis:
            print(f"   ❌ Error: {analysis['error']}")
            continue
        
        print(f"   🔢 Variables: {analysis['total_variables']}")
        print(f"   🔐 Sensitive: {len(analysis['sensitive_variables'])}")
        
        # Check git status
        git_tracked = check_git_status(file_path)
        if git_tracked:
            print(f"   ⚠️  WARNING: File is tracked by Git (should be in .gitignore)")
            security_issues.append(f"{file_path}: Git tracked")
        
        # Show sensitive variables
        if analysis['sensitive_variables']:
            print(f"   🚨 Sensitive variables:")
            for var in analysis['sensitive_variables']:
                print(f"      - {var}")
        
        # Show categories
        print(f"   📂 Variable categories:")
        for category, vars_list in analysis['categories'].items():
            if vars_list:
                print(f"      - {category}: {', '.join(vars_list[:5])}")
                if len(vars_list) > 5:
                    print(f"        ... and {len(vars_list) - 5} more")
        
        # Show content preview
        if analysis['content_preview']:
            print(f"   📄 Content preview:")
            preview_lines = analysis['content_preview'][:200].split('\n')[:3]
            for line in preview_lines:
                if line.strip():
                    print(f"      {line[:80]}{'...' if len(line) > 80 else ''}")
        
        total_vars += analysis['total_variables']
        total_sensitive += len(analysis['sensitive_variables'])
        
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"📁 Total .env files: {len(env_files)}")
    print(f"🔢 Total variables: {total_vars}")
    print(f"🔐 Sensitive variables: {total_sensitive}")
    
    if security_issues:
        print(f"\n⚠️  SECURITY ISSUES:")
        for issue in security_issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ No security issues detected")
    
    # Save detailed report
    report_data = {
        'scan_time': datetime.now().isoformat(),
        'project_root': str(root_path),
        'total_files': len(env_files),
        'total_variables': total_vars,
        'total_sensitive': total_sensitive,
        'security_issues': security_issues,
        'files': []
    }
    
    for file_path in env_files:
        analysis = analyze_env_file(file_path, root_path)
        if 'error' not in analysis:
            report_data['files'].append({
                'name': file_path.name,
                'path': str(file_path),
                'relative_path': analysis['relative_path'],
                'size': analysis['file_size'],
                'modified': analysis['modified_time'].isoformat(),
                'permissions': analysis['permissions'],
                'variables_count': analysis['total_variables'],
                'sensitive_count': len(analysis['sensitive_variables']),
                'sensitive_variables': analysis['sensitive_variables'],
                'categories': analysis['categories'],
                'git_tracked': bool(check_git_status(file_path))
            })
    
    # Save JSON report
    report_file = Path("env_files_scan_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    
    return report_data

def main():
    """Main execution"""
    try:
        # Scan for .env files
        env_files, root_path = scan_env_files()
        
        # Generate report
        report = generate_report(env_files, root_path)
        
        print(f"\n✅ Scan completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()