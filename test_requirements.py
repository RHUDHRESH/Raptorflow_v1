#!/usr/bin/env python3
"""
Test script to verify all requirements can be imported
"""
import sys
import importlib

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠ {module_name}: {e}")
        return False

def main():
    """Test all critical dependencies"""
    print("Testing critical dependencies...")
    
    # Core dependencies
    critical_deps = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'dotenv',
        'supabase',
        'redis',
        'sqlalchemy',
        'razorpay',
        'langchain',
        'openai',
        'tiktoken',
        'aiohttp',
        'tenacity',
        'yaml',  # PyYAML
        'requests',
        'numpy',
        'pandas',
        'httpx',
        'aiofiles',
        'multipart',  # python-multipart
        'bleach',
        'slowapi',
        'prometheus_client',
        'cryptography',
        'jose',  # python-jose
        'passlib',
        'google.auth',
        'jwt',  # pyjwt
        'sklearn',  # scikit-learn
        'chromadb',
        'jinja2',
        'mangum',
        'pytest',
        'structlog',
        'bandit',
        'safety'
    ]
    
    failed = []
    for dep in critical_deps:
        if not test_import(dep):
            failed.append(dep)
    
    print(f"\nResults: {len(critical_deps) - len(failed)}/{len(critical_deps)} imports successful")
    
    if failed:
        print(f"Failed imports: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All critical dependencies can be imported successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
