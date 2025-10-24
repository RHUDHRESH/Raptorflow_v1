#!/usr/bin/env python3
"""
Test script to verify the main FastAPI app can start without errors
"""
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

def test_app_import():
    """Test if the main app can be imported"""
    try:
        # Set minimal environment variables
        os.environ.setdefault('ENVIRONMENT', 'development')
        os.environ.setdefault('PORT', '8080')
        
        # Test import
        from main import app
        print("✓ FastAPI app imported successfully")
        
        # Test app creation
        assert app.title == "RaptorFlow ADAPT API"
        print("✓ App title verified")
        
        # Test routes
        routes = [route.path for route in app.routes]
        assert '/' in routes
        assert '/health' in routes
        print("✓ Core routes verified")
        
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test app startup"""
    print("Testing FastAPI app startup...")
    
    if test_app_import():
        print("\n✅ App startup test passed!")
        print("The application should deploy successfully to GCP Cloud Run.")
        sys.exit(0)
    else:
        print("\n❌ App startup test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
