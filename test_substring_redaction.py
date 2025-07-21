#!/usr/bin/env python3
"""
Test file for substring redaction functionality.
This can be run to verify the implementation works correctly.
"""

import unittest
import sys
import os

# Add the SpectrePDF module to path  
sys.path.insert(0, '/home/runner/work/SpectrePDF/SpectrePDF')

from SpectrePDF.anonymizer import find_substring_matches, calculate_substring_boxes

class TestSubstringRedaction(unittest.TestCase):
    """Test cases for the substring redaction feature."""
    
    def test_github_issue_example(self):
        """Test the exact example from GitHub issue #4."""
        # Test case 1: ABC123DEF456
        matches1 = find_substring_matches("ABC123DEF456", ["123"])
        self.assertEqual(len(matches1), 1)
        self.assertEqual(matches1[0]['start'], 3)
        self.assertEqual(matches1[0]['end'], 6)
        self.assertEqual(matches1[0]['matched_text'], '123')
        
        # Test case 2: 123456
        matches2 = find_substring_matches("123456", ["123"])
        self.assertEqual(len(matches2), 1)
        self.assertEqual(matches2[0]['start'], 0)
        self.assertEqual(matches2[0]['end'], 3)
        self.assertEqual(matches2[0]['matched_text'], '123')
    
    def test_multiple_matches(self):
        """Test text with multiple occurrences of the target."""
        matches = find_substring_matches("123abc123def123", ["123"])
        self.assertEqual(len(matches), 3)
        
        expected_positions = [(0, 3), (6, 9), (12, 15)]
        actual_positions = [(m['start'], m['end']) for m in matches]
        self.assertEqual(actual_positions, expected_positions)
    
    def test_no_matches(self):
        """Test text with no matches."""
        matches = find_substring_matches("abcdefghi", ["123"])
        self.assertEqual(len(matches), 0)
    
    def test_case_insensitive(self):
        """Test that matching is case insensitive."""
        matches = find_substring_matches("ABCdefGHI", ["def"])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['start'], 3)
        self.assertEqual(matches[0]['end'], 6)
    
    def test_overlapping_patterns(self):
        """Test overlapping patterns."""
        matches = find_substring_matches("aaaa", ["aa"])
        # Should find overlapping matches
        self.assertGreaterEqual(len(matches), 2)
    
    def test_box_calculation(self):
        """Test substring box position calculation."""
        word = {'text': 'ABC123DEF456'}
        word_box = {'x': 100, 'y': 50, 'width': 120, 'height': 20}
        
        matches = find_substring_matches(word['text'], ['123'])
        boxes = calculate_substring_boxes(word, word_box, matches)
        
        self.assertEqual(len(boxes), 1)
        
        box = boxes[0]
        # Character width = 120 / 12 = 10 pixels per char
        # Position 3 = 100 + (3 * 10) = 130
        # Width for 3 chars = 3 * 10 = 30
        self.assertEqual(box['x'], 130)
        self.assertEqual(box['width'], 30)
        self.assertEqual(box['y'], 50)
        self.assertEqual(box['height'], 20)
        self.assertEqual(box['matched_text'], '123')
        self.assertEqual(box['target_word'], '123')
    
    def test_multiple_targets(self):
        """Test with multiple target words."""
        matches = find_substring_matches("abc123def456ghi", ["123", "456"])
        self.assertEqual(len(matches), 2)
        
        # Should be sorted by start position
        self.assertEqual(matches[0]['target'], '123')
        self.assertEqual(matches[1]['target'], '456')
    
    def test_empty_string(self):
        """Test with empty string."""
        matches = find_substring_matches("", ["123"])
        self.assertEqual(len(matches), 0)
    
    def test_empty_targets(self):
        """Test with empty target list."""
        matches = find_substring_matches("ABC123DEF456", [])
        self.assertEqual(len(matches), 0)

def run_tests():
    """Run all tests and return success status."""
    print("🧪 Running Substring Redaction Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSubstringRedaction)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests PASSED!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)