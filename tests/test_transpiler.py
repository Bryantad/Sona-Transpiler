"""
Tests for the Sona transpiler core functionality.
"""

import pytest
from sona import SonaToPythonTranspiler
from sona.exceptions import SonaError


class TestSonaToPythonTranspiler:
    """Test the core transpiler functionality."""

    def test_transpiler_initialization(self):
        """Test transpiler can be initialized."""
        transpiler = SonaToPythonTranspiler()
        assert transpiler is not None

    def test_simple_variable_assignment(self, transpiler):
        """Test basic variable assignment transpilation."""
        sona_code = 'let x = 42'
        python_code = transpiler.transpile(sona_code)

        assert 'x = 42' in python_code
        assert python_code.strip()  # Not empty

    def test_simple_function_definition(self, transpiler):
        """Test basic function definition transpilation."""
        sona_code = '''
        func add(a, b) {
            return a + b
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'def add(a, b):' in python_code
        assert 'return a + b' in python_code

    def test_function_with_default_parameters(self, transpiler):
        """Test function with default parameters."""
        sona_code = '''
        func greet(name = "World") {
            print("Hello, " + name + "!")
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'def greet(name=' in python_code
        assert '"World"' in python_code

    def test_control_flow_if_else(self, transpiler):
        """Test if-else statement transpilation."""
        sona_code = '''
        if x > 0 {
            print("positive")
        } else {
            print("non-positive")
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'if x > 0:' in python_code
        assert 'else:' in python_code

    def test_for_loop(self, transpiler):
        """Test for loop transpilation."""
        sona_code = '''
        for i in range(5) {
            print(i)
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'for i in range(5):' in python_code
        assert 'print(i)' in python_code

    def test_while_loop(self, transpiler):
        """Test while loop transpilation."""
        sona_code = '''
        while x < 10 {
            x = x + 1
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'while x < 10:' in python_code
        assert 'x = x + 1' in python_code

    def test_class_definition(self, transpiler):
        """Test class definition transpilation."""
        sona_code = '''
        class Person {
            func init(name) {
                self.name = name
            }

            func greet() {
                print("Hello, I'm " + self.name)
            }
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'class Person:' in python_code
        assert 'def __init__(self, name):' in python_code
        assert 'def greet(self):' in python_code

    def test_list_operations(self, transpiler):
        """Test list creation and operations."""
        sona_code = '''
        let items = [1, 2, 3, 4, 5]
        items.append(6)
        print(items[0])
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'items = [1, 2, 3, 4, 5]' in python_code
        assert 'items.append(6)' in python_code
        assert 'items[0]' in python_code

    def test_dictionary_operations(self, transpiler):
        """Test dictionary creation and operations."""
        sona_code = '''
        let person = {name: "Alice", age: 30}
        print(person["name"])
        person["city"] = "New York"
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'person = {' in python_code
        assert '"name": "Alice"' in python_code
        assert 'person["name"]' in python_code

    def test_error_handling_try_catch(self, transpiler):
        """Test try-catch error handling."""
        sona_code = '''
        try {
            let result = 10 / 0
        } catch (error) {
            print("Error: " + str(error))
        }
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'try:' in python_code
        assert 'except' in python_code

    def test_invalid_syntax_raises_error(self, transpiler):
        """Test that invalid syntax raises appropriate error."""
        invalid_code = '''
        func incomplete_function( {
            // Missing closing parenthesis and parameter
        '''

        with pytest.raises(SonaError):
            transpiler.transpile(invalid_code)

    def test_empty_code(self, transpiler):
        """Test transpiling empty code."""
        python_code = transpiler.transpile("")
        assert python_code is not None
        # Should be empty or minimal boilerplate

    def test_comments_are_preserved(self, transpiler):
        """Test that comments are handled properly."""
        sona_code = '''
        // This is a comment
        let x = 42  // End of line comment
        /* Block comment */
        '''

        python_code = transpiler.transpile(sona_code)
        # Comments might be converted to Python style or stripped
        assert 'x = 42' in python_code

    def test_nested_function_calls(self, transpiler):
        """Test nested function calls."""
        sona_code = '''
        func add(a, b) { return a + b }
        func multiply(a, b) { return a * b }

        let result = add(multiply(2, 3), 4)
        print(result)
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'def add(a, b):' in python_code
        assert 'def multiply(a, b):' in python_code
        assert 'add(multiply(2, 3), 4)' in python_code

    def test_string_interpolation(self, transpiler):
        """Test string operations and concatenation."""
        sona_code = '''
        let name = "Sona"
        let version = "0.7.1"
        let message = "Welcome to " + name + " v" + version
        print(message)
        '''

        python_code = transpiler.transpile(sona_code)
        assert 'name = "Sona"' in python_code
        assert '"Welcome to " + name + " v" + version' in python_code
