"""
Test Runner for HavenMind
Runs all tests and generates comprehensive report
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False, str(e)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking Dependencies...")
    
    required_packages = [
        'flask',
        'sqlite3',
        'requests',
        'pyotp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def run_all_tests():
    """Run comprehensive test suite"""
    print("🧪 HavenMind Complete Test Suite")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 1. Check dependencies
    deps_ok = check_dependencies()
    test_results.append(("Dependencies", deps_ok))
    
    if not deps_ok:
        print("\n❌ Cannot proceed without required dependencies")
        return
    
    # 2. Smoke test
    success, output = run_command("python test_simple.py", "Smoke Test")
    test_results.append(("Smoke Test", success))
    
    # 3. Unit tests
    success, output = run_command("python test_app.py", "Unit Tests")
    test_results.append(("Unit Tests", success))
    
    # 4. Performance test (quick)
    success, output = run_command("python test_performance.py quick", "Performance Test")
    test_results.append(("Performance Test", success))
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY REPORT")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    success_rate = (passed_tests / total_tests) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Your app is ready for deployment.")
    elif success_rate >= 80:
        print("\n⚠️ Most tests passed. Check failed tests before deployment.")
    else:
        print("\n❌ Multiple test failures. Fix issues before deployment.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def run_specific_test(test_type):
    """Run a specific type of test"""
    test_commands = {
        'smoke': ('python test_simple.py', 'Smoke Test'),
        'unit': ('python test_app.py', 'Unit Tests'),
        'manual': ('python test_manual.py', 'Manual Tests'),
        'performance': ('python test_performance.py', 'Performance Tests'),
        'quick-perf': ('python test_performance.py quick', 'Quick Performance Check')
    }
    
    if test_type in test_commands:
        command, description = test_commands[test_type]
        run_command(command, description)
    else:
        print(f"❌ Unknown test type: {test_type}")
        print("Available tests: smoke, unit, manual, performance, quick-perf")

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "all":
            run_all_tests()
        else:
            run_specific_test(test_type)
    else:
        print("🧪 HavenMind Test Runner")
        print("=" * 25)
        print("Usage:")
        print("  python run_tests.py all          # Run all tests")
        print("  python run_tests.py smoke        # Quick smoke test")
        print("  python run_tests.py unit         # Unit tests")
        print("  python run_tests.py manual       # Manual tests")
        print("  python run_tests.py performance  # Performance tests")
        print("  python run_tests.py quick-perf   # Quick performance check")
        print("\nRecommended: Start with 'smoke' then 'all'")

if __name__ == "__main__":
    main()