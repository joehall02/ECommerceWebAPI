import unittest

if __name__ == '__main__':
    # Define the directory where the tests are located
    test_dir = "tests"

    # Define the pattern for the test files
    pattern = "test*.py"

    # Define the verbosity of the test output
    verbosity = 2 # 0 (quiet), 1 (default), 2 (verbose) this means that the output will be more detailed

    test_suite = unittest.TestLoader().discover(start_dir=test_dir, pattern=pattern)
    unittest.TextTestRunner(verbosity=verbosity).run(test_suite)