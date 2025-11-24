import unittest
import os
import shutil
import tempfile
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.workflows import initial_translate
from scripts.app_settings import LANGUAGES

class TestModDiscovery(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the mock source_mod
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source_mod")
        os.makedirs(self.source_dir)
        
        # Mock SOURCE_DIR in initial_translate
        self.original_source_dir = initial_translate.SOURCE_DIR
        initial_translate.SOURCE_DIR = self.source_dir
        
        # Mock game profile
        self.game_profile = {
            "source_localization_folder": "localization",
            "id": "test_game"
        }
        
        self.source_lang = LANGUAGES["1"] # English

    def tearDown(self):
        # Restore SOURCE_DIR
        initial_translate.SOURCE_DIR = self.original_source_dir
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def create_dummy_file(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("l_english:\n key: \"value\"")

    def test_standard_structure(self):
        """Test standard structure: mod/localization/english/test_l_english.yml"""
        mod_name = "StandardMod"
        mod_path = os.path.join(self.source_dir, mod_name)
        loc_path = os.path.join(mod_path, "localization", "english")
        file_path = os.path.join(loc_path, "test_l_english.yml")
        self.create_dummy_file(file_path)

        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["filename"], "test_l_english.yml")
        self.assertTrue(files[0]["path"].endswith("test_l_english.yml"))

    def test_recursive_structure(self):
        """Test EU5 structure: mod/module/localization/english/test_l_english.yml"""
        mod_name = "RecursiveMod"
        mod_path = os.path.join(self.source_dir, mod_name)
        
        # Module 1
        loc_path_1 = os.path.join(mod_path, "in_game", "localization", "english")
        file_path_1 = os.path.join(loc_path_1, "file1_l_english.yml")
        self.create_dummy_file(file_path_1)
        
        # Module 2
        loc_path_2 = os.path.join(mod_path, "main_menu", "localization", "english")
        file_path_2 = os.path.join(loc_path_2, "file2_l_english.yml")
        self.create_dummy_file(file_path_2)

        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        
        self.assertEqual(len(files), 2)
        filenames = sorted([f["filename"] for f in files])
        self.assertEqual(filenames, ["file1_l_english.yml", "file2_l_english.yml"])

    def test_mixed_structure_priority(self):
        """Test that if root localization exists, it ignores sub-modules (Standard Priority)"""
        mod_name = "MixedMod"
        mod_path = os.path.join(self.source_dir, mod_name)
        
        # Root localization (Should be found)
        root_loc_path = os.path.join(mod_path, "localization", "english")
        root_file = os.path.join(root_loc_path, "root_l_english.yml")
        self.create_dummy_file(root_file)
        
        # Sub-module localization (Should be IGNORED if root exists, based on current logic)
        sub_loc_path = os.path.join(mod_path, "sub", "localization", "english")
        sub_file = os.path.join(sub_loc_path, "sub_l_english.yml")
        self.create_dummy_file(sub_file)

        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["filename"], "root_l_english.yml")

    def test_nested_replace_structure(self):
        """Test nested structure: mod/main_menu/localization/english/replace/file.yml"""
        mod_name = "NestedMod"
        mod_path = os.path.join(self.source_dir, mod_name)
        
        # Setup: main_menu/localization/english/replace/
        loc_root = os.path.join(mod_path, "main_menu", "localization")
        loc_path = os.path.join(loc_root, "english", "replace")
        file_path = os.path.join(loc_path, "nested_l_english.yml")
        self.create_dummy_file(file_path)

        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["filename"], "nested_l_english.yml")
        # Verify loc_root is correctly identified as .../main_menu/localization
        self.assertEqual(files[0]["loc_root"], loc_root)

    def test_no_files(self):
        """Test no files found"""
        mod_name = "EmptyMod"
        os.makedirs(os.path.join(self.source_dir, mod_name))
        
        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        self.assertEqual(len(files), 0)

    def test_customizable_localization(self):
        """Test customizable_localization discovery"""
        mod_name = "CustomLocMod"
        mod_path = os.path.join(self.source_dir, mod_name)
        
        cust_loc_path = os.path.join(mod_path, "customizable_localization")
        file_path = os.path.join(cust_loc_path, "test.txt")
        self.create_dummy_file(file_path)

        files = initial_translate.discover_files(mod_name, self.game_profile, self.source_lang)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["filename"], "test.txt")
        self.assertTrue(files[0]["is_custom_loc"])

if __name__ == '__main__':
    unittest.main()
