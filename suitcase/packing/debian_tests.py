"""Tests for the debian packaging class"""


import os
import unittest
from suitcase.packing.debian import Debian

class DebianTestCase(unittest.TestCase):

    """Test suite of tests for the debian packaging class"""

    def assert_equal(self, result, expected):
        """Wraps assertEqual for convenience"""
        return self.assertEqual(
            result,
            expected,
            "%s should be %s" % (result, expected,),
        )

    def setUp(self):
        """Sets up and instantiates the package class"""
        self.deb = Debian()

    def tearDown(self):
        """Tears down the package class"""
        self.deb = None

    def test_invalid_package_name(self):
        """Testing package name validation when package name is invalid"""
        package_name = 'fhjdskfh-900u78*'
        self.assertFalse(self.deb.is_valid_package_name(package_name))

    def test_valid_package_name(self):
        """Testing package name validation when package name is valid"""
        package_name = 'my-awesome-package'
        self.assertTrue(self.deb.is_valid_package_name(package_name))

    def test_package_name_normalisation(self):
        """Test that the package name normalisation works"""
        unnormalised_name = "test_this_test-name"
        expected = "test-this-test-name"
        self.assert_equal(
            self.deb.normalise_package_name(unnormalised_name),
            expected
        )

    def test_package_name_length(self):
        """Test that the package name length is valid"""
        test_string = "A short description"
        self.assertTrue(self.deb.is_valid_description_length(test_string))

    def test_package_name_length2(self):
        """Test that the package name length is invalid when over 60 chars"""

        test_string = "Lorem ipsum dolor sit amet, consectetur adipisicing "\
            "elit, sed do eiusmod tempor incididunt ut labore et dolore magna"\
            " aliqua. Ut enim ad minim veniam, quis nostrud exercitation "\
            "ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis "\
            "aute irure dolor in reprehenderit in voluptate velit esse cillum"\
            " dolore eu fugiat nulla pariatur. Excepteur sint occaecat "\
            "cupidatat non proident, sunt in culpa qui officia deserunt "\
            "mollit anim id est laborum."

        self.assertFalse(self.deb.is_valid_description_length(test_string))

    def test_make_package_name(self):
        """Test package name generation from paths"""
        this_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])
        base_path = os.path.abspath(os.path.realpath(
            os.path.join(this_dir, "../../tests/package_test")
        ))
        path = os.path.join(base_path, "apps/suitcase_test")
        package_name = self.deb.make_package_name(base_path, path)
        expected = "apps-suitcase-test"
        self.assert_equal(package_name, expected)

    def test_make_package_name_wprefix(self):
        """Test package name generation from paths with prefix"""
        this_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])
        base_path = os.path.abspath(os.path.realpath(
            os.path.join(this_dir, "../../tests/package_test")
        ))
        path = os.path.join(base_path, "apps/suitcase_test")
        package_name = self.deb.make_package_name(base_path, path, 'gcap')
        expected = "gcap-apps-suitcase-test"
        self.assert_equal(package_name, expected)

    def test_make_package_name_wfilter(self):
        """Test package name generation from paths with filter"""
        this_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])
        base_path = os.path.abspath(
            os.path.realpath(os.path.join(this_dir, "../../tests/package_test")
        ))
        path = os.path.join(base_path, "apps/suitcase_test")
        package_name = self.deb.make_package_name(
            base_path, path, "gcap", { "suitcase": "awesome" }
        )
        expected = "gcap-apps-awesome-test"
        self.assert_equal(package_name, expected)

suite = unittest.TestLoader().loadTestsFromTestCase(DebianTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)

