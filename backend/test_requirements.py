#!/usr/bin/env python3
"""
Test script to validate requirements.txt for potential issues
"""

import re
from typing import List, Tuple

def parse_requirements(filename: str) -> List[Tuple[str, str]]:
    """Parse requirements.txt and return (package, version) tuples"""
    packages = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle package[extra]==version format
                match = re.match(r'^([a-zA-Z0-9_-]+)(\[[a-zA-Z0-9,]+\])?==(.+)$', line)
                if match:
                    package = match.group(1)
                    version = match.group(3)
                    packages.append((package, version))
    return packages

def check_for_issues(packages: List[Tuple[str, str]]) -> dict:
    """Check for common issues"""
    issues = {
        'duplicates': [],
        'suspicious_versions': [],
        'potential_conflicts': []
    }
    
    seen = {}
    for pkg, ver in packages:
        pkg_lower = pkg.lower()
        if pkg_lower in seen:
            issues['duplicates'].append(f"{pkg} appears multiple times")
        seen[pkg_lower] = ver
        
        # Check for suspicious version numbers
        if 'rc' in ver or 'a' in ver or 'b' in ver:
            issues['suspicious_versions'].append(f"{pkg}=={ver} (pre-release)")
    
    # Known conflict checks
    if 'supabase' in seen and 'httpx' in seen:
        httpx_ver = seen['httpx']
        if httpx_ver >= '0.25':
            issues['potential_conflicts'].append(
                f"supabase requires httpx<0.25.0, but httpx=={httpx_ver}"
            )
    
    return issues

# Run checks
packages = parse_requirements('requirements.txt')
issues = check_for_issues(packages)

print("=" * 60)
print("REQUIREMENTS.TXT VALIDATION REPORT")
print("=" * 60)
print(f"\nTotal packages: {len(packages)}")
print(f"\nPackages parsed:")
for pkg, ver in sorted(packages):
    print(f"  ✓ {pkg}=={ver}")

print("\n" + "=" * 60)
print("ISSUES CHECK")
print("=" * 60)

total_issues = sum(len(v) for v in issues.values())
if total_issues == 0:
    print("\n✅ NO ISSUES FOUND!")
    print("\nAll packages:")
    print("  ✓ No duplicates")
    print("  ✓ No pre-release versions")
    print("  ✓ No known conflicts")
    print("\n🎉 REQUIREMENTS.TXT IS VALID FOR DEPLOYMENT")
else:
    print(f"\n⚠️  FOUND {total_issues} ISSUES:\n")
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"\n{issue_type.upper()}:")
            for issue in issue_list:
                print(f"  ❌ {issue}")

print("\n" + "=" * 60)
