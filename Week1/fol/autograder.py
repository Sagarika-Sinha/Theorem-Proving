import json
import os
import sys
import traceback
from typing import List, Tuple, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fol.robinson import robinson_resolution
    IMPORT_SUCCESS = True
except Exception as e:
    print(f"Error importing robinson.py: {e}")
    print(traceback.format_exc())
    IMPORT_SUCCESS = False
    robinson_resolution = None

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_test_cases(filename: str = "testcases.json") -> List[Dict]:
    """Load test cases from JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get("test_cases", [])
    except FileNotFoundError:
        print(f"{Colors.RED}Error: {filename} not found{Colors.END}")
        return []
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error parsing {filename}: {e}{Colors.END}")
        return []

def format_clauses(clauses: List[List[str]]) -> str:
    """Format clauses for pretty printing."""
    clause_strs = []
    for clause in clauses:
        if not clause:
            clause_strs.append("[]")
        else:
            clause_strs.append(" ∨ ".join(clause))
    return "\n  ".join(clause_strs)

def test_robinson(test_case: Dict) -> Tuple[bool, str, float]:
    """
    Test a single Robinson resolution case.
    
    Returns:
        (passed, message, execution_time)
    """
    import time
    
    test_id = test_case.get("id", "?")
    description = test_case.get("description", "No description")
    clauses = test_case.get("clauses", [])
    expected_result = test_case.get("expected_result", "UNSAT")
    max_iterations = test_case.get("max_iterations", 1000)
    
    try:
        start_time = time.time()
        result, proof = robinson_resolution(clauses, max_iterations=max_iterations)
        execution_time = time.time() - start_time
        
        if result == expected_result:
            message = f"✓ Correct result: {result}"
            if result == "UNSAT":
                if proof and len(proof) > 0:
                    message += f" (proof length: {len(proof)})"
                else:
                    message += " (warning: empty proof)"
            return True, message, execution_time
        else:
            message = f"✗ Expected {expected_result}, got {result}"
            return False, message, execution_time
            
    except NotImplementedError:
        return False, "✗ Function not implemented (raises NotImplementedError)", 0.0
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        return False, f"✗ Exception: {error_msg}", 0.0

def run_test_suite():
    """Run all FOL Robinson resolution tests."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  First-Order Logic - Robinson's Resolution Autograder{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    if not IMPORT_SUCCESS:
        print(f"{Colors.RED}Cannot run tests: Failed to import robinson.py{Colors.END}")
        print(f"{Colors.YELLOW}Make sure robinson.py exists and has no syntax errors.{Colors.END}\n")
        return
    
    # Load test cases
    test_cases = load_test_cases()
    if not test_cases:
        print(f"{Colors.RED}No test cases loaded. Cannot proceed.{Colors.END}\n")
        return
    
    total_passed = 0
    total_tests = len(test_cases)
    total_time = 0.0
    
    for test in test_cases:
        passed, message, exec_time = test_robinson(test)
        total_time += exec_time
        
        status_color = Colors.GREEN if passed else Colors.RED
        print(f"{status_color}Test {test['id']}: {test['description']}{Colors.END}")
        print(f"  Expected: {test['expected_result']} | {message} | Time: {exec_time:.4f}s")
        if 'explanation' in test:
            print(f"  {Colors.CYAN}{test['explanation']}{Colors.END}")
        print()
        
        if passed:
            total_passed += 1
    
    # Print summary
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Total    : {total_passed}/{total_tests} passed ({total_passed/total_tests*100:.1f}%){Colors.END}")
    print(f"{Colors.BOLD}Total execution time: {total_time:.4f}s{Colors.END}\n")
    
    if total_passed == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 Congratulations! All tests passed! 🎉{Colors.END}\n")
    elif total_passed > 0:
        print(f"{Colors.YELLOW}Keep working! {total_tests - total_passed} test(s) still failing.{Colors.END}\n")
    else:
        print(f"{Colors.RED}No tests passed yet. Review the algorithm implementation.{Colors.END}\n")
    
if __name__ == "__main__":
    run_test_suite()
    