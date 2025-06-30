"""
Exception classes for the Sona Transpiler

Provides comprehensive error handling for all stages of transpilation
with detailed error messages and source location tracking.
"""

from typing import Optional, Dict, Any, List


class SonaTranspilerError(Exception):
    """Base exception for all transpiler errors"""

    def __init__(self, message: str, source_location: Optional[str] = None,
                 error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.source_location = source_location
        self.error_code = error_code
        self.context = context or {}

        full_message = message
        if source_location:
            full_message += f" at {source_location}"
        if error_code:
            full_message += f" ({error_code})"

        super().__init__(full_message)


class SonaLexerError(SonaTranspilerError):
    """Error during lexical analysis/tokenization"""

    def __init__(self, message: str, line: int, column: int, token: Optional[str] = None):
        location = f"line {line}, column {column}"
        context = {"line": line, "column": column, "token": token}
        super().__init__(message, location, "LEXER_ERROR", context)


class SonaParserError(SonaTranspilerError):
    """Error during parsing/AST construction"""

    def __init__(self, message: str, line: int, column: int, expected: Optional[List[str]] = None):
        location = f"line {line}, column {column}"
        context = {"line": line, "column": column, "expected": expected}
        super().__init__(message, location, "PARSER_ERROR", context)


class SonaSemanticError(SonaTranspilerError):
    """Error during semantic analysis"""

    def __init__(self, message: str, source_location: Optional[str] = None,
                 symbol: Optional[str] = None):
        context = {"symbol": symbol} if symbol else {}
        super().__init__(message, source_location, "SEMANTIC_ERROR", context)


class SonaCodeGenerationError(SonaTranspilerError):
    """Error during Python code generation"""

    def __init__(self, message: str, ast_node_type: Optional[str] = None):
        context = {"ast_node_type": ast_node_type} if ast_node_type else {}
        super().__init__(message, None, "CODEGEN_ERROR", context)


class SonaRuntimeError(SonaTranspilerError):
    """Error in the runtime bridge system"""

    def __init__(self, message: str, function_name: Optional[str] = None):
        context = {"function_name": function_name} if function_name else {}
        super().__init__(message, None, "RUNTIME_ERROR", context)


class SonaEnvironmentError(SonaTranspilerError):
    """Error in environment/scoping system"""

    def __init__(self, message: str, variable_name: Optional[str] = None,
                 scope_level: Optional[int] = None):
        context = {
            "variable_name": variable_name,
            "scope_level": scope_level
        }
        super().__init__(message, None, "ENVIRONMENT_ERROR", context)


# Utility functions for error formatting
def format_error_with_context(error: SonaTranspilerError, source_code: str) -> str:
    """Format an error with source code context"""
    if not error.source_location or "line" not in error.context:
        return str(error)

    lines = source_code.split('\n')
    line_num = error.context["line"]

    if line_num <= 0 or line_num > len(lines):
        return str(error)

    # Show the problematic line with context
    context_lines = []
    start_line = max(1, line_num - 2)
    end_line = min(len(lines), line_num + 2)

    for i in range(start_line, end_line + 1):
        prefix = ">>> " if i == line_num else "    "
        context_lines.append(f"{prefix}{i:3}: {lines[i-1]}")

    return f"{error}\n\nSource context:\n" + "\n".join(context_lines)


def collect_all_errors(errors: List[SonaTranspilerError]) -> str:
    """Collect and format multiple errors"""
    if not errors:
        return "No errors"

    formatted_errors = []
    for i, error in enumerate(errors, 1):
        formatted_errors.append(f"{i}. {error}")

    return f"Found {len(errors)} error(s):\n" + "\n".join(formatted_errors)
