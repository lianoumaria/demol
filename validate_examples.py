#!/usr/bin/env python3
import os
import sys
import glob
from textx import TextXSemanticError, TextXSyntaxError

# Add the current directory to sys.path to ensure we can import the demol package
sys.path.append(os.getcwd())

try:
    from demol.lang.device import get_device_mm
except ImportError as e:
    print(f"Error importing demol package: {e}")
    print("Make sure you are running this script from the root of the repository.")
    sys.exit(1)

def validate_examples():
    """
    Finds and validates all .dev files in the examples directory.
    """
    examples_dir = os.path.join(os.getcwd(), 'examples')
    if not os.path.exists(examples_dir):
        print(f"Error: Examples directory not found at {examples_dir}")
        sys.exit(1)

    # Find all .dev files recursively
    example_files = glob.glob(os.path.join(examples_dir, '**', '*.dev'), recursive=True)
    
    if not example_files:
        print("No .dev files found in examples directory.")
        sys.exit(0)

    print(f"Found {len(example_files)} example files. Starting validation...\n")

    # Initialize metamodel
    try:
        mm = get_device_mm()
    except Exception as e:
        print(f"Failed to initialize metamodel: {e}")
        sys.exit(1)

    passed = []
    failed = []

    for file_path in sorted(example_files):
        rel_path = os.path.relpath(file_path, os.getcwd())
        print(f"Validating {rel_path}...", end=' ', flush=True)
        
        try:
            mm.model_from_file(file_path)
            print("\033[92m[PASS]\033[0m")
            passed.append(rel_path)
        except (TextXSemanticError, TextXSyntaxError) as e:
            print("\033[91m[FAIL]\033[0m")
            print(f"  Error: {e}")
            failed.append((rel_path, str(e)))
        except Exception as e:
            print("\033[91m[FAIL]\033[0m")
            print(f"  Unexpected Error: {e}")
            failed.append((rel_path, str(e)))

    # Print Summary
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Total Files: {len(example_files)}")
    print(f"Passed:      \033[92m{len(passed)}\033[0m")
    print(f"Failed:      \033[91m{len(failed)}\033[0m")
    
    if failed:
        print("\nFailures:")
        for path, error in failed:
            print(f"- {path}")
            print(f"  {error}")
            print("-" * 30)

    if len(failed) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    validate_examples()
