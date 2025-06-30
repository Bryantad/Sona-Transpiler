# Sona Transpiler

![Version](https://img.shields.io/badge/version-0.7.1-blue.svg)  
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)  
![License](https://img.shields.io/badge/license-MIT-green.svg)  
![Status](https://img.shields.io/badge/status-working-brightgreen.svg)  

A purpose-built, production-grade transpiler that turns Sona code into clean, reliable Python. No fluff—just performant, maintainable code.

---

## What You Get

- **Variable & Constant Mapping**  
  `let x = 42` → `x = 42`  
  `const y = 100` → `y = 100`

- **Full Sona Grammar**  
  All 178 language rules supported, from primitives to classes.

- **Blazing-Fast Parser**  
  Lark-powered: parse in 0.0000–0.0020 s.

- **Source Maps & Error Context**  
  Line/column tracking for easy debugging.

- **CLI + REPL**  
  - `sona run <file>.sona`  
  - `sona transpile in.sona out.py`  
  - `sona repl`  

- **Python API**  
  - `SonaToPythonTranspiler`  
  - `SonaRuntime`  
  - `SonaLexer` / `SonaParser`  

- **Modular Design**  
  Clear separation: lexer → parser → AST → transpiler → runtime.

---

## Installation

### From PyPI  
```bash
pip install sona-transpiler

From Source

git clone https://github.com/Bryantad/Sona-Transpiler.git
cd Sona-Transpiler
pip install -e .

Dev Setup

git clone https://github.com/Bryantad/Sona-Transpiler.git
cd Sona-Transpiler
pip install -e .[dev]


---

Quickstart

CLI

# Execute a Sona script
sona run hello.sona

# Transpile to Python
sona transpile module.sona module.py

# Drop into REPL
sona repl

# Check version
sona --version

Python

from sona import SonaToPythonTranspiler, SonaRuntime

code = """
func greet(name) {
    print("Hi, " + name + "!")
}
greet("Dev")
"""

transpiler = SonaToPythonTranspiler()
py = transpiler.transpile(code)

runtime = SonaRuntime()
runtime.execute(py)


---

Language Coverage

Primitives: numbers, strings, booleans

Data Structures: arrays, dictionaries

Control Flow: if/else, for, while, break/continue

Functions: parameters, defaults, closures, recursion

Classes: methods, inheritance, self

Modules: import/export, built-ins

Error Handling: try/catch, stack traces



---

Project Layout

sona/
├── cli.py             # entry points
├── lexer.py           # token definitions
├── parser.py          # Lark grammar + AST builder
├── ast_nodes.py       # typed AST classes
├── transpiler.py      # core Sona→Python logic
├── runtime.py         # execution bridge
├── environment.py     # scopes & variables
├── source_mapper.py   # mapping back to Sona
└── exceptions.py      # granular error types


---

Performance

Transpilation: >6 000 ops/sec

Parse Time: ~1 – 2 ms per file

Memory: lean AST, on-demand node creation

Startup: lazy-load modules for sub-100 ms CLI launch



---

Tests & QA

# Install dev deps
pip install -r requirements-dev.txt

# Run unit + integration tests
pytest --cov=sona --cov-report=html

We enforce formatting with Black, lint with Flake8, and type-check via MyPy.


---

Docs & Examples

Language Guide: docs/language_guide.md

API Reference: docs/api_reference.md

Examples: examples/*.sona

Contributing: CONTRIBUTING.md



---

Changelog

Detailed history in CHANGELOG.md. We follow Keep a Changelog + SemVer.


---

License

Sona Transpiler © 2025 Netcore Solutions LLC (a Waycore Inc. subsidiary)
MIT License — see LICENSE.
