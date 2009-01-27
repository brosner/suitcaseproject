"""Tests for the debian packaging class"""

import os
import sys
import unittest
import shutil
import commands

from suitcase.utils.copy import copy_files
from suitcase.utils.common import (
    remove_leading_slash, 
    dynamic_import, 
    add_trailing_slash, 
    get_dynamic_class_instance, 
    relative_import, 
    get_user_input, 
    run_command, 
    merge_and_de_dupe, 
    merge
)


class UtilsTestCase(unittest.TestCase):
    
    """Tests for utils"""
    
    def assert_equal(self, result, expected):
        """Wraps assertEqual for convenience"""
        return self.assertEqual(
            result,
            expected,
            "%s should be %s" % (result, expected,),
        )

    def test_strip_leading_slash(self):
        """test stripping of the leading slash"""
        test = remove_leading_slash(" /win")
        expected = "win"
        self.assert_equal(test, expected)

    def test_strip_leading_slash2(self):
        """test stripping of the leading slash with leading + trailing space"""
        test = remove_leading_slash(" /win ")
        expected = "win"
        self.assert_equal(test, expected)

    def test_strip_leading_slash3(self):
        """testing stripping a non-existent slash"""
        test = remove_leading_slash("win")
        expected = "win"
        self.assert_equal(test, expected)

    def test_add_trailing_slash(self):
        """testing adding a slash"""
        test = add_trailing_slash("win")
        expected = "win/"
        self.assert_equal(test, expected)

    def test_add_trailing_slash2(self):
        """testing adding a slash to a string that already has a slash"""
        test = add_trailing_slash("win/")
        expected = "win/"
        self.assert_equal(test, expected)

    def test_dynamic_import(self):
        """Test the dynamic import works"""
        import_string = "suitcase.vcs.subversion"
        module = dynamic_import(import_string)
        self.assert_equal(import_string, module.__name__)

    def test_get_dynamic_class_instance(self):
        """Test the dynamic instance creation works"""
        import_string = "suitcase.vcs.subversion"
        instance = get_dynamic_class_instance(import_string, "Subversion")
        self.assertTrue(isinstance(instance, instance.__class__))

    def test_singleton_works(self):
        """Test singleton instance creation"""
        import_string = "suitcase.vcs.subversion"
        module = dynamic_import(import_string)
        # Create first instance
        instance = module.Subversion()
        # Create Second instance
        instance2 = module.Subversion()
        # Both instances should occupy the same memory space
        self.assert_equal(instance, instance2)

    def test_relative_import(self):
        """tests that an arbitrary path can be imported into a namespace

        Relative import is basically a way of aliasing a namespace

        """
        test_path = os.path.join(os.path.dirname(__file__), "../tests")
        module = relative_import(test_path, "fail")
        self.assert_equal(module, sys.modules["fail"])

    @staticmethod
    def clean_up_copy():
        """Removes the copy dir"""
        test_dir_a = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                "../tests/copy_test/A/"
            )
        )
        shutil.rmtree(test_dir_a)

    def test_copy(self):
        """Tests that files are copied successfully"""
        test_dir_a = os.path.join(
            os.path.dirname(__file__), "../tests/copy_test/A"
        )
        test_dir_b = os.path.join(
            os.path.dirname(__file__), "../tests/copy_test/B/"
        )
        os.makedirs(test_dir_a)
        copy_files(test_dir_b, test_dir_a)
        file_list = commands.getstatusoutput("ls %s" % test_dir_a)[1].split()
        self.clean_up_copy()
        self.assert_equal(file_list, ['test1.txt', 'test2.txt', 'test_dir'])

    def test_copy2(self):
        """Tests that files are copied successfully with exclusions"""
        test_dir_a = os.path.join(
            os.path.dirname(__file__), "../tests/copy_test/A"
        )
        test_dir_b = os.path.join(
            os.path.dirname(__file__), "../tests/copy_test/B/"
        )
        os.makedirs(test_dir_a)
        copy_files(test_dir_b, test_dir_a, exclusions=["test2.txt"])
        file_list = commands.getstatusoutput("ls %s" % test_dir_a)[1].split()
        self.clean_up_copy()
        self.assert_equal(file_list, ['test1.txt', 'test_dir'])

    @staticmethod
    def raw_input_mock_n(prompt):
        """mock of raw_input returns 'n'"""
        return "n"

    @staticmethod
    def raw_input_mock_enter(prompt):
        """mock of raw_input returns ''"""
        return ""

    def test_raw_input(self):
        """Check getting user input"""
        suitcase.utils.raw_input = self.raw_input_mock_n
        answer = get_user_input('Is this awesome or what?', ["y", "n"])
        self.assert_equal(answer, 'n')

    def test_raw_input2(self):
        """Test getting user input with default"""
        suitcase.utils.raw_input = self.raw_input_mock_enter
        answer = get_user_input('Is this awesome or what?', ["y", "n"], "n")
        self.assert_equal(answer, 'n')

    def test_run_command(self):
        """testing running a typical command"""
        command = "ls"
        result = run_command(command)
        self.assert_equal(result[0], 0)


    def test_list_merge(self):
        """testing merging lists 1"""
        list1 = [1, 3]
        list2 = [1, 2, 2, 3, 4]
        new_list = merge(list1, list2)
        self.assert_equal(new_list, [1, 3, 1, 2, 2, 3, 4])
        
    def test_list_merge_and_de_dupe1(self):
        """testing merging +deduping lists 1"""
        list1 = [1, 3]
        list2 = [1, 2, 2, 3, 4]
        new_list = merge_and_de_dupe(list1, list2)
        self.assert_equal(new_list, [1, 3, 2, 4])

    def test_list_merge_and_de_dupe2(self):
        """testing merging + deduping lists 2"""
        list1 = 1
        list2 = [2, 2, 3, 4]
        new_list = merge_and_de_dupe(list1, list2)
        self.assert_equal(new_list, [1, 2, 3, 4])


TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
unittest.TextTestRunner(verbosity=2).run(TEST_SUITE)

