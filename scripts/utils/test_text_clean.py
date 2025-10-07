# scripts/utils/test_text_clean.py

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.utils.text_clean import strip_outer_quotes, strip_pl_diacritics

class TestStripOuterQuotes(unittest.TestCase):

    def test_matched_double_quotes(self):
        self.assertEqual(strip_outer_quotes('"Hello World"'), "Hello World")

    def test_matched_polish_quotes(self):
        self.assertEqual(strip_outer_quotes('„Hello World”'), "Hello World")

    def test_matched_guillemets(self):
        self.assertEqual(strip_outer_quotes('«Hello World»'), "Hello World")

    def test_mismatched_quotes(self):
        self.assertEqual(strip_outer_quotes('"Hello World”'), '"Hello World”')

    def test_no_quotes(self):
        self.assertEqual(strip_outer_quotes("Hello World"), "Hello World")

    def test_single_quote_at_start(self):
        self.assertEqual(strip_outer_quotes('"Hello World'), '"Hello World')

    def test_single_quote_at_end(self):
        self.assertEqual(strip_outer_quotes('Hello World"'), 'Hello World"')

    def test_empty_string(self):
        self.assertEqual(strip_outer_quotes(""), "")

    def test_only_quotes(self):
        self.assertEqual(strip_outer_quotes('""'), "")

    def test_internal_quotes(self):
        self.assertEqual(strip_outer_quotes('"He said "hello""'), 'He said "hello"')

class TestStripPlDiacritics(unittest.TestCase):

    def test_polish_diacritics(self):
        self.assertEqual(strip_pl_diacritics("zażółć gęślą jaźń"), "zazolc gesla jazn")

    def test_mixed_diacritics(self):
        self.assertEqual(strip_pl_diacritics("ZAŻÓŁĆ GĘŚLĄ JAŹŃ"), "ZAZOLC GESLA JAZN")

    def test_no_diacritics(self):
        self.assertEqual(strip_pl_diacritics("Hello World"), "Hello World")

    def test_other_language_diacritics(self):
        self.assertEqual(strip_pl_diacritics("你好世界"), "你好世界")
        self.assertEqual(strip_pl_diacritics("Привет, мир"), "Привет, мир")

    def test_empty_string(self):
        self.assertEqual(strip_pl_diacritics(""), "")

if __name__ == '__main__':
    unittest.main()
