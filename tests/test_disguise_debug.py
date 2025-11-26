import sys
import scripts.workflows.initial_translate as initial_translate_module

def test_import_and_run_existence():
    print("DEBUG: Module:", initial_translate_module)
    print("DEBUG: Dir:", dir(initial_translate_module))
    assert hasattr(initial_translate_module, 'run')
    print("DEBUG: Run function:", initial_translate_module.run)
