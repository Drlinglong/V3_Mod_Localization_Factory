import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from scripts.workflows import initial_translate
    print(f"Module imported: {initial_translate}")
    if hasattr(initial_translate, 'run'):
        print("Function 'run' exists.")
    else:
        print("Function 'run' DOES NOT exist.")
        print(dir(initial_translate))
except Exception as e:
    print(f"Import failed: {e}")
