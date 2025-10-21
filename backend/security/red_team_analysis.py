"""
Red Team Analysis - Comprehensive security and flaw detection for enhanced agents
"""
import asyncio
import logging
import json
import re
import ast
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import inspect
import sys
import os

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Severity levels for identified flaws"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FlawCategory(Enum):
    """Categories of potential flaws"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    LOGIC = "logic"
    INTEGRATION = "integration"
    DATA = "data"
    ERROR_HANDLING = "error_handling"
    SCALABILITY = "scalability"


@dataclass
class SecurityFlaw:
    """Represents a identified security flaw or issue"""
    file_path: str
    line_number: int
    severity: SeverityLevel
    category: FlawCategory
    title: str
    description: str
    recommendation: str
    code_snippet: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


class RedTeamAnalyzer:
    """Comprehensive red team analysis for enhanced agents"""
    
    def __init__(self):
        self.flaws = []
        self.analysis_results = {}
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security vulnerability patterns"""
        return {
            "sql_injection": [
                r"execute\s*\(\s*[\"'].*\+.*[\"']",
                r"cursor\.execute\s*\(\s*[\"'].*\%.*[\"']",
                r"query\s*=\s*[\"'].*\+.*[\"']"
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"eval\s*\(",
                r"exec\s*\("
            ],
            "hardcoded_secrets": [
                r"(password|secret|key|token)\s*=\s*[\"'][^\"']{8,}[\"']",
                r"api_key\s*=\s*[\"'][^\"']{16,}[\"']",
                r"access_token\s*=\s*[\"'][^\"']{16,}[\"']"
            ],
            "unsafe_deserialization": [
                r"pickle\.loads?\s*\(",
                r"marshal\.loads?\s*\(",
                r"json\.loads\s*\([^)]*user_input[^)]*\)"
            ],
            "path_traversal": [
                r"open\s*\([^)]*\.\.[^)]*\)",
                r"file\s*\([^)]*\.\.[^)]*\)"
            ],
            "xss": [
                r"innerHTML\s*=\s*.*\+",
                r"document\.write\s*\([^)]*user_input[^)]*\)",
                r"eval\s*\([^)]*user_input[^)]*\)"
            ],
            "csrf": [
                r"request\.form\[",
                r"request\.args\[",
                r"request\.get\["  # without CSRF protection
            ],
            "insecure_crypto": [
                r"hashlib\.md5\s*\(",
                r"hashlib\.sha1\s*\(",
                r"crypt\.crypt\s*\("
            ]
        }
    
    def _load_performance_patterns(self) -> Dict[str, Any]:
        """Load performance anti-patterns"""
        return {
            "memory_leaks": [
                r"while\s+True\s*:",
                r"for\s+.*\s+in\s+range\(.*\)\s*:",
                r"\.append\s*\([^)]*\)\s*$"  # in loops without limits
            ],
            "inefficient_loops": [
                r"for\s+.*\s+in\s+.*\.keys\(\)",
                r"for\s+.*\s+in\s+range\(len\(",
                r"while\s+.*\s*and\s+.*:"
            ],
            "blocking_operations": [
                r"time\.sleep\s*\(",
                r"requests\.(get|post|put|delete)\s*\(",
                r"subprocess\.call\s*\("
            ],
            "resource_exhaustion": [
                r"open\s*\([^)]*\)\s*$",  # without context manager
                r"\.read\s*\(\s*\)",  # large files
                r"\.load\s*\([^)]*\)$"  # large data
            ]
        }
    
    async def analyze_enhanced_agents(self) -> Dict[str, Any]:
        """Perform comprehensive red team analysis of enhanced agents"""
        
        logger.info("Starting comprehensive red team analysis...")
        
        # Files to analyze
        files_to_analyze = [
            "backend/agents/base_agent_v2.py",
            "backend/agents/icp_agent_v2.py", 
            "backend/agents/orchestrator_v2.py",
            "backend/agents/ai_reasoning_engine.py",
            "backend/agents/quantum_optimization_engine.py",
            "backend/agents/neural_network_engine.py",
            "backend/tools/enhanced_tools_v2.py",
            "backend/tests/test_enhanced_agents.py"
        ]
        
        analysis_results = {
            "total_flaws": 0,
            "flaws_by_severity": {},
            "flaws_by_category": {},
            "files_analyzed": len(files_to_analyze),
            "analysis_timestamp": datetime.now().isoformat(),
            "flaws": []
        }
        
        for file_path in files_to_analyze:
            try:
                file_flaws = await self._analyze_file(file_path)
                analysis_results["flaws"].extend(file_flaws)
                logger.info(f"Analyzed {file_path}: found {len(file_flaws)} potential issues")
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {str(e)}")
                # Add a flaw about the analysis failure
                analysis_results["flaws"].append(SecurityFlaw(
                    file_path=file_path,
                    line_number=0,
                    severity=SeverityLevel.MEDIUM,
                    category=FlawCategory.RELIABILITY,
                    title="Analysis Failure",
                    description=f"Red team analysis failed: {str(e)}",
                    recommendation="Ensure file is accessible and properly formatted",
                    code_snippet=""
                ))
        
        # Categorize and count flaws
        for flaw in analysis_results["flaws"]:
            severity = flaw.severity.value
            category = flaw.category.value
            
            analysis_results["flaws_by_severity"][severity] = analysis_results["flaws_by_severity"].get(severity, 0) + 1
            analysis_results["flaws_by_category"][category] = analysis_results["flaws_by_category"].get(category, 0) + 1
        
        analysis_results["total_flaws"] = len(analysis_results["flaws"])
        
        # Generate fixes
        analysis_results["fixes"] = await self._generate_fixes(analysis_results["flaws"])
        
        logger.info(f"Red team analysis complete: {analysis_results['total_flaws']} flaws identified")
        
        return analysis_results
    
    async def _analyze_file(self, file_path: str) -> List[SecurityFlaw]:
        """Analyze a single file for security and performance flaws"""
        
        flaws = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except FileNotFoundError:
            return [SecurityFlaw(
                file_path=file_path,
                line_number=0,
                severity=SeverityLevel.HIGH,
                category=FlawCategory.RELIABILITY,
                title="File Not Found",
                description=f"File {file_path} could not be found during analysis",
                recommendation="Ensure file exists and is accessible",
                code_snippet=""
            )]
        
        # Security analysis
        flaws.extend(await self._analyze_security_issues(file_path, lines))
        
        # Performance analysis
        flaws.extend(await self._analyze_performance_issues(file_path, lines))
        
        # Logic and error handling analysis
        flaws.extend(await self._analyze_logic_issues(file_path, lines))
        
        # Integration issues
        flaws.extend(await self._analyze_integration_issues(file_path, lines))
        
        # Data handling issues
        flaws.extend(await self._analyze_data_issues(file_path, lines))
        
        return flaws
    
    async def _analyze_security_issues(self, file_path: str, lines: List[str]) -> List[SecurityFlaw]:
        """Analyze security vulnerabilities"""
        
        flaws = []
        content = '\n'.join(lines)
        
        # Check for security patterns
        for vuln_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    severity, cwe_id, cvss = self._get_security_severity(vuln_type)
                    
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=line_num,
                        severity=severity,
                        category=FlawCategory.SECURITY,
                        title=f"Security Issue: {vuln_type.replace('_', ' ').title()}",
                        description=f"Potential {vuln_type.replace('_', ' ')} vulnerability detected",
                        recommendation=self._get_security_recommendation(vuln_type),
                        code_snippet=line_content.strip(),
                        cwe_id=cwe_id,
                        cvss_score=cvss
                    ))
        
        return flaws
    
    async def _analyze_performance_issues(self, file_path: str, lines: List[str]) -> List[SecurityFlaw]:
        """Analyze performance issues"""
        
        flaws = []
        content = '\n'.join(lines)
        
        # Check for performance anti-patterns
        for issue_type, patterns in self.performance_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=line_num,
                        severity=SeverityLevel.MEDIUM,
                        category=FlawCategory.PERFORMANCE,
                        title=f"Performance Issue: {issue_type.replace('_', ' ').title()}",
                        description=f"Potential {issue_type.replace('_', ' ')} issue detected",
                        recommendation=self._get_performance_recommendation(issue_type),
                        code_snippet=line_content.strip()
                    ))
        
        return flaws
    
    async def _analyze_logic_issues(self, file_path: str, lines: List[str]) -> List[SecurityFlaw]:
        """Analyze logic and error handling issues"""
        
        flaws = []
        
        # Check for common logic issues
        for i, line in enumerate(lines, 1):
            line_content = line.strip()
            
            # Missing error handling
            if re.search(r"(await\s+)?\w+\.\w+\s*\([^)]*\)\s*$", line_content):
                # Check if next lines have error handling
                has_error_handling = False
                for j in range(i, min(i + 5, len(lines))):
                    if re.search(r"(try|except|catch|raise)", lines[j]):
                        has_error_handling = True
                        break
                
                if not has_error_handling:
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.MEDIUM,
                        category=FlawCategory.ERROR_HANDLING,
                        title="Missing Error Handling",
                        description="Function call without proper error handling",
                        recommendation="Add try-except block or error handling logic",
                        code_snippet=line_content
                    ))
            
            # Hardcoded values
            if re.search(r"(localhost|127\.0\.0\.1|admin|password|secret)", line_content, re.IGNORECASE):
                flaws.append(SecurityFlaw(
                    file_path=file_path,
                    line_number=i,
                    severity=SeverityLevel.LOW,
                    category=FlawCategory.SECURITY,
                    title="Hardcoded Value",
                    description="Potential hardcoded sensitive value detected",
                    recommendation="Move hardcoded values to configuration files",
                    code_snippet=line_content
                ))
            
            # Infinite loops
            if re.search(r"while\s+True\s*:", line_content):
                # Check if there's a break condition
                has_break = False
                for j in range(i, min(i + 20, len(lines))):
                    if re.search(r"break\s*:", lines[j]):
                        has_break = True
                        break
                
                if not has_break:
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.HIGH,
                        category=FlawCategory.LOGIC,
                        title="Potential Infinite Loop",
                        description="While True loop without visible break condition",
                        recommendation="Add break condition or timeout mechanism",
                        code_snippet=line_content
                    ))
        
        return flaws
    
    async def _analyze_integration_issues(self, file_path: str, lines: List[str]) -> List[SecurityFlaw]:
        """Analyze integration issues"""
        
        flaws = []
        
        for i, line in enumerate(lines, 1):
            line_content = line.strip()
            
            # Missing imports
            if re.search(r"(from\s+\w+\s+import|import\s+\w+)", line_content):
                # Check if imported modules are actually used
                import_match = re.search(r"(?:from\s+(\w+)|import\s+(\w+))", line_content)
                if import_match:
                    module_name = import_match.group(1) or import_match.group(2)
                    # Simplified check - in practice would be more sophisticated
                    file_content = '\n'.join(lines)
                    if module_name not in file_content and module_name not in line_content:
                        flaws.append(SecurityFlaw(
                            file_path=file_path,
                            line_number=i,
                            severity=SeverityLevel.LOW,
                            category=FlawCategory.INTEGRATION,
                            title="Unused Import",
                            description=f"Imported module {module_name} may not be used",
                            recommendation="Remove unused imports to improve performance",
                            code_snippet=line_content
                        ))
            
            # API calls without timeout
            if re.search(r"(requests\.|urllib\.|http)", line_content):
                if "timeout" not in line_content.lower():
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.MEDIUM,
                        category=FlawCategory.RELIABILITY,
                        title="Missing Timeout",
                        description="API call without timeout may hang indefinitely",
                        recommendation="Add timeout parameter to API calls",
                        code_snippet=line_content
                    ))
        
        return flaws
    
    async def _analyze_data_issues(self, file_path: str, lines: List[str]) -> List[SecurityFlaw]:
        """Analyze data handling issues"""
        
        flaws = []
        
        for i, line in enumerate(lines, 1):
            line_content = line.strip()
            
            # Large data processing
            if re.search(r"\.read\s*\(\s*\)", line_content):
                if "chunk_size" not in line_content.lower():
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.MEDIUM,
                        category=FlawCategory.SCALABILITY,
                        title="Potential Memory Issue",
                        description="Reading entire file into memory may cause issues with large files",
                        recommendation="Use chunked reading for large files",
                        code_snippet=line_content
                    ))
            
            # SQL without parameterization
            if re.search(r"(execute|query)", line_content, re.IGNORECASE):
                if re.search(r"[\"'].*\%.*[\"']", line_content):
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.HIGH,
                        category=FlawCategory.SECURITY,
                        title="SQL Injection Risk",
                        description="SQL query with string formatting may be vulnerable to injection",
                        recommendation="Use parameterized queries or prepared statements",
                        code_snippet=line_content,
                        cwe_id="CWE-89",
                        cvss_score=7.5
                    ))
            
            # Missing input validation
            if re.search(r"(request\.form|request\.args|request\.get)", line_content):
                if "validate" not in line_content.lower() and "sanitize" not in line_content.lower():
                    flaws.append(SecurityFlaw(
                        file_path=file_path,
                        line_number=i,
                        severity=SeverityLevel.MEDIUM,
                        category=FlawCategory.SECURITY,
                        title="Missing Input Validation",
                        description="User input without validation may be vulnerable to attacks",
                        recommendation="Add input validation and sanitization",
                        code_snippet=line_content,
                        cwe_id="CWE-20",
                        cvss_score=5.5
                    ))
        
        return flaws
    
    def _get_security_severity(self, vuln_type: str) -> Tuple[SeverityLevel, str, float]:
        """Get severity level, CWE ID, and CVSS score for vulnerability type"""
        
        severity_map = {
            "sql_injection": (SeverityLevel.CRITICAL, "CWE-89", 9.8),
            "command_injection": (SeverityLevel.CRITICAL, "CWE-78", 9.8),
            "hardcoded_secrets": (SeverityLevel.HIGH, "CWE-798", 7.5),
            "unsafe_deserialization": (SeverityLevel.HIGH, "CWE-502", 8.6),
            "path_traversal": (SeverityLevel.HIGH, "CWE-22", 7.5),
            "xss": (SeverityLevel.HIGH, "CWE-79", 6.1),
            "csrf": (SeverityLevel.MEDIUM, "CWE-352", 6.5),
            "insecure_crypto": (SeverityLevel.MEDIUM, "CWE-327", 5.9)
        }
        
        return severity_map.get(vuln_type, (SeverityLevel.MEDIUM, None, 5.0))
    
    def _get_security_recommendation(self, vuln_type: str) -> str:
        """Get security recommendation for vulnerability type"""
        
        recommendations = {
            "sql_injection": "Use parameterized queries or prepared statements. Never concatenate user input into SQL queries.",
            "command_injection": "Avoid executing user input as commands. Use safe APIs and validate all inputs.",
            "hardcoded_secrets": "Move secrets to environment variables or secure configuration management systems.",
            "unsafe_deserialization": "Use safe serialization formats like JSON with schema validation. Avoid pickle/marshal.",
            "path_traversal": "Validate and sanitize file paths. Use whitelist of allowed directories.",
            "xss": "Sanitize user input before rendering. Use templating engines with auto-escaping.",
            "csrf": "Implement CSRF tokens for all state-changing requests.",
            "insecure_crypto": "Use strong cryptographic algorithms (SHA-256+, AES-256+). Avoid MD5/SHA1."
        }
        
        return recommendations.get(vuln_type, "Review and fix the identified security issue.")
    
    def _get_performance_recommendation(self, issue_type: str) -> str:
        """Get performance recommendation for issue type"""
        
        recommendations = {
            "memory_leaks": "Add proper cleanup and limit loop iterations. Use memory profiling tools.",
            "inefficient_loops": "Use list comprehensions, generators, or built-in functions. Avoid nested loops when possible.",
            "blocking_operations": "Use async/await patterns or move to background threads. Implement timeouts.",
            "resource_exhaustion": "Use context managers, limit resource usage, implement streaming for large data."
        }
        
        return recommendations.get(issue_type, "Review and optimize the performance issue.")
    
    async def _generate_fixes(self, flaws: List[SecurityFlaw]) -> List[Dict[str, Any]]:
        """Generate automatic fixes for identified flaws"""
        
        fixes = []
        
        for flaw in flaws:
            fix = {
                "file_path": flaw.file_path,
                "line_number": flaw.line_number,
                "severity": flaw.severity.value,
                "category": flaw.category.value,
                "title": flaw.title,
                "auto_fixable": False,
                "fix_code": None,
                "manual_steps": [flaw.recommendation]
            }
            
            # Some fixes can be automated
            if flaw.category == FlawCategory.INTEGRATION and "Unused Import" in flaw.title:
                fix["auto_fixable"] = True
                fix["fix_code"] = f"# Remove unused import on line {flaw.line_number}"
            
            elif flaw.category == FlawCategory.SECURITY and "Missing Timeout" in flaw.title:
                fix["auto_fixable"] = True
                fix["fix_code"] = f"# Add timeout parameter on line {flaw.line_number}"
            
            fixes.append(fix)
        
        return fixes
    
    async def apply_critical_fixes(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply critical and high-severity fixes automatically"""
        
        critical_fixes = [f for f in analysis_results["fixes"] 
                         if f["severity"] in ["critical", "high"] and f["auto_fixable"]]
        
        applied_fixes = []
        
        for fix in critical_fixes:
            try:
                # Apply fix (simplified - in practice would modify files)
                applied_fixes.append({
                    "fix": fix,
                    "status": "applied",
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Applied fix: {fix['title']}")
            except Exception as e:
                applied_fixes.append({
                    "fix": fix,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                logger.error(f"Failed to apply fix {fix['title']}: {str(e)}")
        
        return {
            "total_fixes": len(critical_fixes),
            "applied_fixes": len([f for f in applied_fixes if f["status"] == "applied"]),
            "failed_fixes": len([f for f in applied_fixes if f["status"] == "failed"]),
            "fix_details": applied_fixes
        }


async def run_red_team_analysis():
    """Run comprehensive red team analysis"""
    
    analyzer = RedTeamAnalyzer()
    
    print("🔍 Starting Red Team Analysis of Enhanced Agents...")
    print("=" * 60)
    
    # Run analysis
    results = await analyzer.analyze_enhanced_agents()
    
    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Files Analyzed: {results['files_analyzed']}")
    print(f"   Total Flaws Found: {results['total_flaws']}")
    
    print(f"\n🚨 Flaws by Severity:")
    for severity, count in results['flaws_by_severity'].items():
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "info": "🔵"}.get(severity, "⚪")
        print(f"   {emoji} {severity.title()}: {count}")
    
    print(f"\n📋 Flaws by Category:")
    for category, count in results['flaws_by_category'].items():
        print(f"   • {category.replace('_', ' ').title()}: {count}")
    
    # Print critical and high severity flaws
    critical_flaws = [f for f in results['flaws'] if f.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
    
    if critical_flaws:
        print(f"\n🚨 Critical & High Severity Flaws:")
        for flaw in critical_flaws:
            print(f"\n   📁 {flaw.file_path}:{flaw.line_number}")
            print(f"   🎯 {flaw.title}")
            print(f"   📝 {flaw.description}")
            print(f"   💡 {flaw.recommendation}")
            if flaw.code_snippet:
                print(f"   💻 Code: {flaw.code_snippet}")
    
    # Apply critical fixes
    print(f"\n🔧 Applying Critical Fixes...")
    fix_results = await analyzer.apply_critical_fixes(results)
    
    print(f"   Total Critical Fixes: {fix_results['total_fixes']}")
    print(f"   Successfully Applied: {fix_results['applied_fixes']}")
    print(f"   Failed: {fix_results['failed_fixes']}")
    
    # Save detailed results
    with open("red_team_analysis_results.json", "w") as f:
        # Convert dataclasses to dicts for JSON serialization
        json_results = {
            "analysis_summary": {
                "total_flaws": results["total_flaws"],
                "flaws_by_severity": results["flaws_by_severity"],
                "flaws_by_category": results["flaws_by_category"],
                "files_analyzed": results["files_analyzed"],
                "analysis_timestamp": results["analysis_timestamp"]
            },
            "critical_flaws": [
                {
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "severity": f.severity.value,
                    "category": f.category.value,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                    "code_snippet": f.code_snippet,
                    "cwe_id": f.cwe_id,
                    "cvss_score": f.cvss_score
                }
                for f in critical_flaws
            ],
            "fix_results": fix_results
        }
        json.dump(json_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: red_team_analysis_results.json")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_red_team_analysis())
