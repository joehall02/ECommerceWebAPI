import pytest

if __name__ == '__main__':
    pytest.main(['tests', '-p', 'no:warnings']) # Run the tests in the tests directory and ignore the warnings
    # pytest.main(['tests']) # Run the tests in the tests directory 