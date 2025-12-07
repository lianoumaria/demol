import os
import glob
from demol.lang.device import get_device_mm

def verify_all_examples():
    print("Initializing device metamodel...")
    try:
        mm = get_device_mm()
    except Exception as e:
        print(f"Failed to initialize metamodel: {e}")
        return

    examples_dir = "examples"
    dev_files = glob.glob(os.path.join(examples_dir, "**/*.dev"), recursive=True)
    
    print(f"Found {len(dev_files)} example files.")
    
    passed = 0
    failed = 0
    
    for dev_file in dev_files:
        print(f"Verifying {dev_file}...")
        try:
            model = mm.model_from_file(dev_file)
            print(f"  [PASS] {dev_file}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {dev_file}")
            print(f"    Error: {e}")
            failed += 1
            
    print("-" * 40)
    print(f"Verification Complete.")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        exit(1)

if __name__ == "__main__":
    verify_all_examples()
