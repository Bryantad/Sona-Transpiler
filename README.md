# Sona Transpiler

![Version](https://img.shields.io/badge/version-0.7.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A focused, production-grade transpiler for the Sona programming language that converts Sona code to Python with high performance and reliability.

## 🚀 Features

-   **High Performance**: 6,106+ operations per second baseline
-   **Complete Grammar Support**: All 178 Sona language grammar rules
-   **Source Mapping**: Detailed debugging information and error tracking
-   **CLI Interface**: Run, transpile, and REPL modes
-   **Modular Architecture**: Clean separation of concerns
-   **Error Handling**: Comprehensive error reporting with context
-   **Type Safety**: Full type hints for better development experience

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install sona-transpiler
```

### From Source

```bash
git clone https://github.com/Bryantad/Sona-Transpiler.git
cd Sona-Transpiler
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/Bryantad/Sona-Transpiler.git
cd Sona-Transpiler
pip install -e .[dev]
```

## 🔧 Usage

### Command Line Interface

#### Run a Sona File

```bash
sona run script.sona
```

#### Transpile to Python

```bash
sona transpile input.sona output.py
```

#### Interactive REPL

```bash
sona repl
```

#### Show Version

```bash
sona --version
```

### Python API

```python
from sona import SonaToPythonTranspiler, SonaRuntime

# Create transpiler instance
transpiler = SonaToPythonTranspiler()

# Transpile Sona code to Python
sona_code = '''
func greet(name) {
    print("Hello, " + name + "!")
}

greet("World")
'''

python_code = transpiler.transpile(sona_code)
print(python_code)

# Execute with runtime
runtime = SonaRuntime()
runtime.execute(python_code)
```

## 📋 Language Support

The Sona Transpiler supports the complete Sona language specification:

### Variables and Data Types

```sona
let name = "Sona"
let age = 25
let is_active = true
let items = [1, 2, 3, 4, 5]
let person = {name: "Alice", age: 30}
```

### Functions

```sona
func add(a, b) {
    return a + b
}

func greet(name = "World") {
    print("Hello, " + name + "!")
}
```

### Control Flow

```sona
if age >= 18 {
    print("Adult")
} else {
    print("Minor")
}

for i in range(5) {
    print(i)
}

while x < 10 {
    x = x + 1
}
```

### Classes and Objects

```sona
class Person {
    func init(name, age) {
        self.name = name
        self.age = age
    }

    func greet() {
        print("Hi, I'm " + self.name)
    }
}

let p = Person("Alice", 25)
p.greet()
```

## 🏗️ Architecture

The Sona Transpiler is built with a modular architecture:

```
sona/
├── __init__.py          # Package exports and metadata
├── cli.py               # Command-line interface
├── lexer.py             # Tokenization and lexical analysis
├── parser.py            # AST construction with Lark
├── ast_nodes.py         # AST node hierarchy
├── transpiler.py        # Core Sona→Python transpiler
├── runtime.py           # Python execution runtime
├── environment.py       # Scoping and variable management
├── source_mapper.py     # Source mapping for debugging
└── exceptions.py        # Error handling system
```

## 🔬 Performance

The Sona Transpiler maintains high performance standards:

-   **Transpilation Speed**: 6,106+ operations per second
-   **Memory Efficient**: Optimized AST and environment management
-   **Fast Parsing**: Lark-based parser with grammar optimization
-   **Minimal Overhead**: Direct Python code generation

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=sona --cov-report=html
```

## 📚 Documentation

-   [Language Guide](docs/language_guide.md) - Complete Sona language reference
-   [API Reference](docs/api_reference.md) - Python API documentation
-   [Examples](examples/) - Sample Sona programs
-   [Contributing](CONTRIBUTING.md) - Development guidelines

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/Sona-Transpiler.git`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

### Code Style

We use Black for code formatting and Flake8 for linting:

```bash
black sona/
flake8 sona/
mypy sona/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

-   **GitHub**: https://github.com/Bryantad/Sona-Transpiler
-   **PyPI**: https://pypi.org/project/sona-transpiler/
-   **Issues**: https://github.com/Bryantad/Sona-Transpiler/issues
-   **Discussions**: https://github.com/Bryantad/Sona-Transpiler/discussions

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## 🙏 Acknowledgments

-   Built with [Lark](https://github.com/lark-parser/lark) parsing toolkit
-   Inspired by modern transpiler design patterns
-   Thanks to all contributors and users

---

**Sona Transpiler** - Bringing Sona to Python with speed and reliability.
