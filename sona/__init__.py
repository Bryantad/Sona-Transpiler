"""
Sona Transpiler Package v0.7.1

A research-grade transpiler for the Sona programming language targeting Python.
Converts Sona source code to equivalent Python code for improved performance
and seamless integration with the Python ecosystem.

Key Features:
- Multi-stage transpilation pipeline (Parse → AST → CodeGen)
- Performance-optimized execution (6,106+ ops/sec baseline)
- Complete Sona language support (178 grammar rules)
- Source mapping for debugging support
- Runtime bridge system for Sona-specific features

Components:
- lexer.py: Tokenization and lexical analysis
- parser.py: AST construction using Lark grammar
- ast_nodes.py: AST node hierarchy with visitor pattern
- transpiler.py: Main SonaToPythonTranspiler class
- runtime.py: SonaRuntime bridge to Python
- environment.py: Environment/scoping system
- source_mapper.py: Source mapping for debugging
"""

__version__ = "0.7.1"
__author__ = "Sona Language Team"
__license__ = "MIT"

__all__ = [
    "SonaToPythonTranspiler",
    "SonaRuntime",
    "SonaLexer",
    "SonaParser",
    "Environment",
    "SourceMapper",
    "transpile_code",
    "transpile_file",
    "SonaTranspilerError",
    "main"
]

from .transpiler import SonaToPythonTranspiler, transpile_code, transpile_file
from .runtime import SonaRuntime
from .lexer import SonaLexer
from .parser import SonaParser
from .environment import Environment
from .source_mapper import SourceMapper
from .exceptions import SonaTranspilerError
from .cli import main

# Package metadata
PERFORMANCE_BASELINE = 6106  # ops/sec minimum requirement
SUPPORTED_GRAMMAR_RULES = 178
PYTHON_TARGET_VERSION = "3.8+"
