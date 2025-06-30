# Contributing to Sona Transpiler

Thank you for your interest in contributing to the Sona Transpiler! This document provides guidelines and information for contributors.

## 🎯 Getting Started

### Prerequisites

-   Python 3.8 or higher
-   Git
-   Basic understanding of transpilers/compilers
-   Familiarity with the Sona programming language

### Development Setup

1. **Fork the repository**

    ```bash
    # Go to https://github.com/Bryantad/Sona-Transpiler and click "Fork"
    ```

2. **Clone your fork**

    ```bash
    git clone https://github.com/yourusername/Sona-Transpiler.git
    cd Sona-Transpiler
    ```

3. **Install development dependencies**

    ```bash
    pip install -r requirements-dev.txt
    pip install -e .
    ```

4. **Verify installation**
    ```bash
    sona --version
    pytest
    ```

## 🏗️ Development Workflow

### Code Style

We use several tools to maintain code quality:

-   **Black**: Code formatting
-   **Flake8**: Linting and style checking
-   **MyPy**: Type checking
-   **pytest**: Testing

Run all checks:

```bash
# Format code
black sona/ tests/

# Check linting
flake8 sona/ tests/

# Type checking
mypy sona/

# Run tests
pytest --cov=sona
```

### Making Changes

1. **Create a feature branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Make your changes**

    - Write code following the existing patterns
    - Add tests for new functionality
    - Update documentation as needed

3. **Test your changes**

    ```bash
    pytest
    black sona/ tests/
    flake8 sona/ tests/
    mypy sona/
    ```

4. **Commit your changes**

    ```bash
    git add .
    git commit -m "Add feature: your feature description"
    ```

5. **Push and create a pull request**
    ```bash
    git push origin feature/your-feature-name
    # Then create a PR on GitHub
    ```

## 📋 Types of Contributions

### 🐛 Bug Reports

When reporting bugs, please include:

-   **Clear description** of the issue
-   **Steps to reproduce** the problem
-   **Expected vs actual behavior**
-   **Sona code sample** that demonstrates the issue
-   **Environment details** (Python version, OS, etc.)

Use the bug report template when creating issues.

### ✨ Feature Requests

For new features, please:

-   **Check existing issues** to avoid duplicates
-   **Describe the use case** and why it's needed
-   **Provide examples** of how it would work
-   **Consider implementation** complexity and compatibility

### 📚 Documentation

Documentation improvements are always welcome:

-   Fix typos or unclear explanations
-   Add examples and usage patterns
-   Improve API documentation
-   Create tutorials or guides

### 🧪 Tests

Test contributions help improve reliability:

-   Add tests for edge cases
-   Improve test coverage
-   Create performance benchmarks
-   Add integration tests

## 🔧 Technical Guidelines

### Code Organization

The codebase follows this structure:

```
sona/
├── __init__.py          # Package exports
├── cli.py               # Command-line interface
├── lexer.py             # Tokenization
├── parser.py            # AST construction
├── ast_nodes.py         # AST node definitions
├── transpiler.py        # Core transpilation logic
├── runtime.py           # Python execution bridge
├── environment.py       # Scoping and variables
├── source_mapper.py     # Source location tracking
└── exceptions.py        # Error handling
```

### Adding New Language Features

When adding support for new Sona language features:

1. **Update the grammar** in `grammar/sona.lark`
2. **Add AST nodes** in `ast_nodes.py`
3. **Implement parsing** in `parser.py`
4. **Add transpilation** in `transpiler.py`
5. **Update runtime** if needed in `runtime.py`
6. **Add comprehensive tests**

### Performance Considerations

The transpiler maintains a performance baseline of 6,106+ ops/sec:

-   **Profile changes** that might affect performance
-   **Use efficient algorithms** and data structures
-   **Minimize memory allocations** in hot paths
-   **Add benchmarks** for performance-critical code

### Error Handling

Follow these patterns for error handling:

-   **Use specific exception types** from `exceptions.py`
-   **Include source location** information when possible
-   **Provide helpful error messages** with context
-   **Test error conditions** thoroughly

## 🧪 Testing Guidelines

### Test Structure

Tests are organized by component:

```
tests/
├── test_lexer.py           # Lexer tests
├── test_parser.py          # Parser tests
├── test_transpiler.py      # Transpiler tests
├── test_runtime.py         # Runtime tests
├── test_cli.py             # CLI tests
├── integration/            # End-to-end tests
└── benchmarks/             # Performance tests
```

### Writing Tests

-   **Test both success and failure cases**
-   **Use descriptive test names**
-   **Include edge cases and boundary conditions**
-   **Test error messages and exception types**
-   **Add docstrings explaining complex test scenarios**

Example test:

```python
def test_function_with_default_parameters():
    """Test transpilation of functions with default parameters."""
    sona_code = '''
    func greet(name = "World") {
        print("Hello, " + name + "!")
    }
    '''

    transpiler = SonaToPythonTranspiler()
    python_code = transpiler.transpile(sona_code)

    # Should generate valid Python with default arguments
    assert "def greet(name='World'):" in python_code
    assert "print('Hello, ' + name + '!')" in python_code
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_transpiler.py

# Run with coverage
pytest --cov=sona --cov-report=html

# Run performance tests
pytest tests/benchmarks/ -v
```

## 📝 Documentation

### Code Documentation

-   **Add docstrings** to all public functions and classes
-   **Use type hints** consistently
-   **Document complex algorithms** with inline comments
-   **Include examples** in docstrings when helpful

### External Documentation

-   **Update README.md** for user-facing changes
-   **Update CHANGELOG.md** for all changes
-   **Add examples** to the `examples/` directory
-   **Update API documentation** for new features

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

-   **MAJOR**: Incompatible API changes
-   **MINOR**: New functionality (backward compatible)
-   **PATCH**: Bug fixes (backward compatible)

### Release Checklist

Before creating a release:

1. **Update version** in `sona/__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** and ensure all tests pass
4. **Check performance benchmarks** meet baseline
5. **Update documentation** as needed
6. **Create GitHub release** with proper tags

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

-   **Be respectful** and considerate
-   **Be collaborative** and helpful
-   **Focus on constructive feedback**
-   **Welcome newcomers** and different perspectives

### Communication

-   **GitHub Issues**: Bug reports and feature requests
-   **GitHub Discussions**: General questions and ideas
-   **Pull Requests**: Code contributions and reviews

### Review Process

All contributions go through code review:

-   **Automated checks** must pass (tests, linting, etc.)
-   **Manual review** by maintainers
-   **Feedback incorporation** and iteration
-   **Final approval** and merge

## 🙏 Recognition

Contributors are recognized in several ways:

-   **CONTRIBUTORS.md**: List of all contributors
-   **GitHub releases**: Mention of significant contributions
-   **Documentation**: Credit for major features or improvements

## 📞 Getting Help

If you need help:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for specific problems

---

Thank you for contributing to the Sona Transpiler! Every contribution, no matter how small, helps make the project better for everyone.
