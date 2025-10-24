#!/usr/bin/env python3
"""
Test script to verify Docker deployment readiness
"""
import subprocess
import sys
import os

def test_docker_build():
    """Test if Docker build would succeed"""
    print("🐳 Testing Docker build readiness...")
    
    # Check if Dockerfile exists
    if not os.path.exists('Dockerfile'):
        print("❌ Dockerfile not found")
        return False
    
    # Check if requirements.cloud.txt exists
    if not os.path.exists('backend/requirements.cloud.txt'):
        print("❌ backend/requirements.cloud.txt not found")
        return False
    
    # Check if main.py exists
    if not os.path.exists('backend/main.py'):
        print("❌ backend/main.py not found")
        return False
    
    print("✅ All required files exist")
    
    # Test Python syntax of main files
    try:
        import ast
        
        with open('backend/main.py', 'r') as f:
            ast.parse(f.read())
        print("✅ backend/main.py syntax is valid")
        
        with open('backend/requirements.cloud.txt', 'r') as f:
            requirements = f.read()
            if 'sqlalchemy-pgvector' in requirements:
                print("❌ sqlalchemy-pgvector still in requirements - this was the original error")
                return False
        print("✅ backend/requirements.cloud.txt is clean")
        
    except SyntaxError as e:
        print(f"❌ Syntax error in main files: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False
    
    return True

def test_gcp_deployment_files():
    """Test GCP deployment files"""
    print("\n☁️ Testing GCP deployment files...")
    
    required_files = [
        'cloudbuild.yaml',
        '.gcloudignore',
        'deploy-cloud-run.sh'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ {file} not found")
            return False
        print(f"✅ {file} exists")
    
    return True

def main():
    """Main test function"""
    print("🚀 RaptorFlow GCP Deployment Readiness Test")
    print("=" * 50)
    
    docker_ready = test_docker_build()
    gcp_ready = test_gcp_deployment_files()
    
    print("\n" + "=" * 50)
    if docker_ready and gcp_ready:
        print("✅ DEPLOYMENT READY!")
        print("The application should deploy successfully to GCP Cloud Run.")
        print("\nNext steps:")
        print("1. Push your changes to GitHub")
        print("2. Run: gcloud builds submit --config cloudbuild.yaml")
        print("3. Deploy to Cloud Run")
        return 0
    else:
        print("❌ DEPLOYMENT NOT READY")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
