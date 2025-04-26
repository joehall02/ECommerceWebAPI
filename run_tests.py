import sys
import pytest

if __name__ == '__main__':
    # pytest.main(['tests', '-p', 'no:warnings']) # Run the tests in the tests directory and ignore the warnings
    # pytest.main(['tests']) # Run the tests in the tests directory 

    # Run tests with --maxfail=1 to stop at the first failure, and --disable-warnings to suppress warnings
    # We can also use --exitfirst to stop immediately after the first failure
    result = pytest.main(['tests', '--maxfail=1', '--disable-warnings', '--exitfirst'])
    
    # If pytest fails, exit with the same status code as pytest
    sys.exit(result)