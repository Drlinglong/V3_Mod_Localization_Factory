import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from scripts.core.glossary_manager import glossary_manager

print(f"Checking glossaries for 'stellaris'...")
glossaries = glossary_manager.get_available_glossaries('stellaris')
print(f"Result: {glossaries}")

print(f"Checking glossaries for '2' (just in case)...")
glossaries_2 = glossary_manager.get_available_glossaries('2')
print(f"Result for '2': {glossaries_2}")
