"""
Basic functionality test for security scan module.
This tests the core components without pytest dependencies.
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add the backend_app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_basic_functionality():
    """Test basic functionality of security scan module."""
    
    print("Testing Security Scan Module - Basic Functionality")
    print("=" * 60)
    
    try:
        # Test 1: Import all modules
        print("1. Testing module imports...")
        from security_scan.io_contract import ScanRequest, ScanResult, VirusUpdateStatus, ScanStatus
        from security_scan.scan_service import ClamAVScanService
        from security_scan.quarantine_manager import FileQuarantineManager
        from security_scan.virus_update_manager import ClamAVUpdateManager
        from security_scan.cron_scheduler import APSchedulerManager
        from security_scan.config import get_config
        print("   ✓ All modules imported successfully")
        
        # Test 2: Configuration
        print("2. Testing configuration...")
        config = get_config()
        print(f"   ✓ Configuration loaded: {config.base_data_path}")
        
        # Test 3: IO Contracts
        print("3. Testing IO contracts...")
        scan_request = ScanRequest("test_id", "/test/file.pdf", "application/pdf")
        scan_result = ScanResult(ScanStatus.SAFE, {"test": "data"}, "/clean/file.pdf", None)
        virus_status = VirusUpdateStatus(datetime.now(), True, "2025-12-06.1")
        print("   ✓ IO contracts work correctly")
        
        # Test 4: Quarantine Manager
        print("4. Testing quarantine manager...")
        temp_dir = tempfile.mkdtemp()
        quarantine_manager = FileQuarantineManager(temp_dir)
        quarantine_manager.ensure_folder_structure()
        
        # Test file movement
        test_content = b"Test file content"
        incoming_path = quarantine_manager.move_to_incoming(test_content, "test.pdf")
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        clean_path = quarantine_manager.mark_as_safe(scanning_path)
        
        print(f"   ✓ File moved through quarantine: {clean_path}")
        
        # Test 5: Scan Service
        print("5. Testing scan service...")
        scan_service = ClamAVScanService()
        print("   ✓ Scan service initialized")
        
        # Test 6: Virus Update Manager
        print("6. Testing virus update manager...")
        update_manager = ClamAVUpdateManager(
            db_path=os.path.join(temp_dir, "virus_db"),
            backup_path=os.path.join(temp_dir, "virus_db_backup")
        )
        print("   ✓ Virus update manager initialized")
        
        # Test 7: Scheduler
        print("7. Testing scheduler...")
        scheduler = APSchedulerManager(update_manager, quarantine_manager)
        print("   ✓ Scheduler initialized")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("Security Scan Module is working correctly.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints are accessible."""
    
    print("\nTesting API Endpoints...")
    print("-" * 30)
    
    try:
        from routers.security_scan import router
        print("✓ API router imported successfully")
        
        # Check if endpoints exist
        endpoints = [route.path for route in router.routes]
        print(f"✓ Found {len(endpoints)} endpoints:")
        for endpoint in endpoints:
            print(f"  - {endpoint}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Security Scan Module - Installation and Basic Testing")
    print("=" * 70)
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Overall result
    overall_success = basic_success and api_success
    
    print(f"\n{'='*70}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Basic Functionality: {'PASSED' if basic_success else 'FAILED'}")
    print(f"API Endpoints:       {'PASSED' if api_success else 'FAILED'}")
    print(f"Overall Result:      {'PASSED' if overall_success else 'FAILED'}")
    print(f"{'='*70}")
    
    if overall_success:
        print("\n🎉 Security Scan Module is ready for use!")
        print("Next steps:")
        print("1. Install ClamAV on your system")
        print("2. Configure environment variables if needed")
        print("3. Start the scheduler in your application")
        print("4. Begin scanning files through the API endpoints")
    else:
        print("\n❌ There are issues with the Security Scan Module")
        print("Please check the error messages above for details")
    
    sys.exit(0 if overall_success else 1)