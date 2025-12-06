"""
Simple test runner for security scan module tests.
This avoids pytest compatibility issues and runs tests directly.
"""

import sys
import os
import unittest
import tempfile
import shutil

# Add the backend_app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def run_security_scan_tests():
    """Run all security scan tests."""
    
    # Import test modules
    try:
        from security_scan.tests.test_safe_file_scan import TestSafeFileScan
        from security_scan.tests.test_infected_file_scan import TestInfectedFileScan
        from security_scan.tests.test_quarantine_movement import TestQuarantineMovement
        from security_scan.tests.test_virus_db_validation import TestVirusDBValidation
        from security_scan.tests.test_daily_scheduler import TestDailyScheduler
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add tests
        suite.addTest(unittest.makeSuite(TestSafeFileScan))
        suite.addTest(unittest.makeSuite(TestInfectedFileScan))
        suite.addTest(unittest.makeSuite(TestQuarantineMovement))
        suite.addTest(unittest.makeSuite(TestVirusDBValidation))
        suite.addTest(unittest.makeSuite(TestDailyScheduler))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\n{'='*60}")
        print("SECURITY SCAN MODULE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
        
        if result.failures:
            print(f"\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print(f"\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
        
        success = len(result.failures) == 0 and len(result.errors) == 0
        print(f"\nOverall Result: {'PASSED' if success else 'FAILED'}")
        
        return success
        
    except ImportError as e:
        print(f"Error importing test modules: {e}")
        print("Make sure you're running this from the Backend/backend_app directory")
        return False

if __name__ == "__main__":
    success = run_security_scan_tests()
    sys.exit(0 if success else 1)