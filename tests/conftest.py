"""
Test configuration and fixtures for Sona Transpiler tests.
"""

import pytest
from pathlib import Path

from sona import SonaToPythonTranspiler, SonaRuntime, SonaLexer, SonaParser


@pytest.fixture
def transpiler():
    """Create a SonaToPythonTranspiler instance for testing."""
    return SonaToPythonTranspiler()


@pytest.fixture
def runtime():
    """Create a SonaRuntime instance for testing."""
    return SonaRuntime()


@pytest.fixture
def lexer():
    """Create a SonaLexer instance for testing."""
    return SonaLexer()


@pytest.fixture
def parser():
    """Create a SonaParser instance for testing."""
    return SonaParser()


@pytest.fixture
def sample_sona_code():
    """Sample Sona code for testing."""
    return '''
    func greet(name = "World") {
        print("Hello, " + name + "!")
    }

    let x = 42
    let y = x + 8
    print(y)

    greet("Sona")
    '''


@pytest.fixture
def complex_sona_code():
    """Complex Sona code for testing advanced features."""
    return '''
    class Calculator {
        func init() {
            self.history = []
        }

        func add(a, b) {
            let result = a + b
            self.history.append("add: " + str(a) + " + " + str(b) + " = " + str(result))
            return result
        }

        func get_history() {
            return self.history
        }
    }

    let calc = Calculator()
    let sum = calc.add(10, 5)
    print("Result: " + str(sum))

    for entry in calc.get_history() {
        print(entry)
    }
    '''


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


def get_test_file_path(filename: str) -> Path:
    """Get the path to a test data file."""
    return TEST_DATA_DIR / filename


# Common test utilities
def assert_valid_python(code: str):
    """Assert that generated code is valid Python."""
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        pytest.fail(f"Generated Python code is invalid: {e}\nCode:\n{code}")


def assert_transpilation_works(transpiler, sona_code: str):
    """Assert that Sona code transpiles successfully."""
    try:
        python_code = transpiler.transpile(sona_code)
        assert_valid_python(python_code)
        return python_code
    except Exception as e:
        pytest.fail(f"Transpilation failed: {e}\nSona code:\n{sona_code}")


def assert_execution_works(runtime, python_code: str):
    """Assert that Python code executes successfully."""
    try:
        result = runtime.execute(python_code)
        return result
    except Exception as e:
        pytest.fail(f"Execution failed: {e}\nPython code:\n{python_code}")
