"""
Main Transpiler Implementation for Sona→Python

This module provides the core SonaToPythonTranspiler class that coordinates
the entire transpilation process from Sona source code to executable Python.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import time
from .parser import SonaParser
from .ast_nodes import *
from .environment import EnvironmentManager
from .source_mapper import SourceMapper
from .exceptions import *


class SonaToPythonTranspiler:
    """
    Main transpiler class - AST to Python code generation

    Converts Sona AST nodes to equivalent Python code while maintaining
    Sona semantics and providing debugging support through source mapping.
    """

    def __init__(self, enable_optimizations: bool = True, enable_source_maps: bool = True):
        """
        Initialize transpiler

        Args:
            enable_optimizations: Enable code optimizations
            enable_source_maps: Generate source maps for debugging
        """
        self.parser = SonaParser()
        self.environment_manager = EnvironmentManager()
        self.source_mapper = SourceMapper()
        self.enable_optimizations = enable_optimizations
        self.enable_source_maps = enable_source_maps

        # Code generation state
        self.current_indent = 0
        self.indent_size = 4
        self.generated_code: List[str] = []

        # Performance tracking
        self.transpilation_stats = {
            "parse_time": 0.0,
            "transpile_time": 0.0,
            "total_time": 0.0,
            "nodes_processed": 0,
            "lines_generated": 0
        }

    def transpile(self, sona_code: str, filename: str = "<string>") -> Dict[str, Any]:
        """
        Transpile Sona code to Python

        Args:
            sona_code: Sona source code
            filename: Source filename for debugging

        Returns:
            Transpilation result dictionary
        """
        start_time = time.time()

        try:
            # Parse Sona code to AST
            parse_start = time.time()
            ast = self.parser.parse(sona_code, filename)
            parse_time = time.time() - parse_start

            # Add source file to mapper
            if self.enable_source_maps:
                self.source_mapper.add_source_file(filename, sona_code)

            # Transpile AST to Python
            transpile_start = time.time()
            self._reset_generation_state()
            python_code = self._visit_program(ast)
            transpile_time = time.time() - transpile_start

            total_time = time.time() - start_time

            # Update stats
            self.transpilation_stats.update({
                "parse_time": parse_time,
                "transpile_time": transpile_time,
                "total_time": total_time,
                "lines_generated": len(self.generated_code)
            })

            return {
                "success": True,
                "python_code": python_code,
                "source_map": self.source_mapper.generate_source_map() if self.enable_source_maps else None,
                "stats": self.transpilation_stats.copy(),
                "ast": ast
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "python_code": "",
                "stats": self.transpilation_stats.copy()
            }

    def _reset_generation_state(self):
        """Reset code generation state"""
        self.current_indent = 0
        self.generated_code = []
        self.environment_manager = EnvironmentManager()
        if self.enable_source_maps:
            self.source_mapper.reset()

    def _emit(self, code: str, source_location: Optional[tuple] = None):
        """Emit Python code with optional source mapping"""
        if source_location and self.enable_source_maps:
            line, column = source_location
            self.source_mapper.map_location(line, column)

        self.generated_code.append(" " * self.current_indent + code)

        if self.enable_source_maps:
            self.source_mapper.advance_generated_position(code + "\n")

    def _emit_line(self, code: str = "", source_location: Optional[tuple] = None):
        """Emit a line of Python code"""
        self._emit(code, source_location)

    def _indent(self):
        """Increase indentation"""
        self.current_indent += self.indent_size

    def _dedent(self):
        """Decrease indentation"""
        self.current_indent = max(0, self.current_indent - self.indent_size)

    # AST Visitor methods
    def _visit_program(self, node: Program) -> str:
        """Visit program node"""
        # Emit runtime imports
        self._emit_line("# Auto-generated from Sona source code")
        self._emit_line("from sona.runtime import *")
        self._emit_line()

        # Visit all statements
        for statement in node.statements:
            self._visit_statement(statement)

        return "\n".join(self.generated_code)

    def _visit_statement(self, node):
        """Visit statement node"""
        if isinstance(node, Assignment):
            self._visit_assignment(node)
        elif isinstance(node, ExpressionStatement):
            self._visit_expression_statement(node)
        elif isinstance(node, PrintStatement):
            self._visit_print_statement(node)
        elif isinstance(node, IfStatement):
            self._visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self._visit_while_statement(node)
        elif isinstance(node, FunctionDef):
            self._visit_function_def(node)
        elif isinstance(node, ReturnStatement):
            self._visit_return_statement(node)
        elif isinstance(node, Expression):
            # Handle expressions as expression statements
            self._visit_expression(node)
        else:
            # Try to emit as string if it's not recognized
            self._emit_line(f"# Unknown node type: {type(node)}")
            self._emit_line(str(node))

    def _visit_assignment(self, node: Assignment):
        """Visit assignment node"""
        source_location = (node.line, node.column)

        # Generate Python assignment
        value_code = self._visit_expression(node.value)

        if node.is_declaration:
            # Variable declaration
            self._emit_line(f"{node.target} = {value_code}", source_location)
            self.environment_manager.get_current_environment().define(node.target, None)
        else:
            # Variable assignment
            self._emit_line(f"{node.target} = {value_code}", source_location)
            self.environment_manager.get_current_environment().assign(node.target, None)

    def _visit_expression_statement(self, node: ExpressionStatement):
        """Visit expression statement"""
        expr_code = self._visit_expression(node.expression)
        self._emit_line(expr_code)

    def _visit_print_statement(self, node: PrintStatement):
        """Visit print statement"""
        if not node.arguments:
            self._emit_line("print()")
        else:
            args = [self._visit_expression(arg) for arg in node.arguments]
            args_str = ", ".join(args)
            self._emit_line(f"print({args_str})")

    def _visit_if_statement(self, node: IfStatement):
        """Visit if statement"""
        condition_code = self._visit_expression(node.condition)
        self._emit_line(f"if {condition_code}:")

        self._indent()
        for stmt in node.then_branch:
            self._visit_statement(stmt)
        self._dedent()

        if node.else_branch:
            self._emit_line("else:")
            self._indent()
            for stmt in node.else_branch:
                self._visit_statement(stmt)
            self._dedent()

    def _visit_while_statement(self, node: WhileStatement):
        """Visit while statement"""
        condition_code = self._visit_expression(node.condition)
        self._emit_line(f"while {condition_code}:")

        self._indent()
        for stmt in node.body:
            self._visit_statement(stmt)
        self._dedent()

    def _visit_function_def(self, node: FunctionDef):
        """Visit function definition"""
        params = ", ".join(node.parameters)
        self._emit_line(f"def {node.name}({params}):")

        self._indent()
        # Create function environment
        func_env = self.environment_manager.push_function_environment(node.name)

        # Define parameters in function scope
        for param in node.parameters:
            func_env.define(param, None)

        # Visit function body
        for stmt in node.body:
            self._visit_statement(stmt)

        # Pop function environment
        self.environment_manager.pop_environment()
        self._dedent()
        self._emit_line()

    def _visit_return_statement(self, node: ReturnStatement):
        """Visit return statement"""
        if node.value:
            value_code = self._visit_expression(node.value)
            self._emit_line(f"return {value_code}")
        else:
            self._emit_line("return")

    def _visit_expression(self, node: Expression) -> str:
        """Visit expression node and return generated code"""
        if isinstance(node, Literal):
            return self._visit_literal(node)
        elif isinstance(node, Identifier):
            return self._visit_identifier(node)
        elif isinstance(node, BinaryOp):
            return self._visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self._visit_unary_op(node)
        elif isinstance(node, FunctionCall):
            return self._visit_function_call(node)
        elif isinstance(node, ArrayLiteral):
            return self._visit_array_literal(node)
        else:
            raise SonaCodeGenerationError(f"Unsupported expression type: {type(node)}")

    def _visit_literal(self, node: Literal) -> str:
        """Visit literal node"""
        if isinstance(node.value, str):
            # Handle string literals
            if node.type_hint == "f_string":
                # F-string interpolation - simplified for now
                return f'f"{node.value}"'
            else:
                return repr(node.value)
        elif node.value is None:
            return "None"
        else:
            return str(node.value)

    def _visit_identifier(self, node: Identifier) -> str:
        """Visit identifier node"""
        # Check if variable is defined
        if not self.environment_manager.get_current_environment().is_defined(node.name):
            # Could be a built-in or forward reference
            pass

        return node.name

    def _visit_binary_op(self, node: BinaryOp) -> str:
        """Visit binary operation node"""
        left_code = self._visit_expression(node.left)
        right_code = self._visit_expression(node.right)

        # Map Sona operators to Python
        operator_map = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "==": "==",
            "!=": "!=",
            ">": ">",
            "<": "<",
            ">=": ">=",
            "<=": "<=",
            "&&": " and ",
            "||": " or "
        }

        python_op = operator_map.get(node.operator, node.operator)
        return f"({left_code} {python_op} {right_code})"

    def _visit_unary_op(self, node: UnaryOp) -> str:
        """Visit unary operation node"""
        operand_code = self._visit_expression(node.operand)

        if node.operator == "!":
            return f"not {operand_code}"
        elif node.operator == "-":
            return f"-{operand_code}"
        else:
            return f"{node.operator}{operand_code}"

    def _visit_function_call(self, node: FunctionCall) -> str:
        """Visit function call node"""
        function_code = self._visit_expression(node.function)
        args = [self._visit_expression(arg) for arg in node.arguments]
        args_str = ", ".join(args)
        return f"{function_code}({args_str})"

    def _visit_array_literal(self, node: ArrayLiteral) -> str:
        """Visit array literal node"""
        elements = [self._visit_expression(elem) for elem in node.elements]
        elements_str = ", ".join(elements)
        return f"[{elements_str}]"


# Convenience functions
def transpile_code(sona_code: str, filename: str = "<string>",
                  enable_optimizations: bool = True) -> Dict[str, Any]:
    """
    Transpile Sona code to Python

    Args:
        sona_code: Sona source code
        filename: Source filename
        enable_optimizations: Enable code optimizations

    Returns:
        Transpilation result
    """
    transpiler = SonaToPythonTranspiler(enable_optimizations=enable_optimizations)
    return transpiler.transpile(sona_code, filename)


def transpile_file(input_file: Union[str, Path], output_file: Optional[Union[str, Path]] = None,
                  enable_optimizations: bool = True) -> Dict[str, Any]:
    """
    Transpile Sona file to Python

    Args:
        input_file: Input Sona file path
        output_file: Output Python file path (optional)
        enable_optimizations: Enable code optimizations

    Returns:
        Transpilation result
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read Sona source code
    with open(input_path, 'r', encoding='utf-8') as f:
        sona_code = f.read()

    # Transpile
    result = transpile_code(sona_code, str(input_path), enable_optimizations)

    # Write output if specified
    if output_file and result["success"]:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["python_code"])

    return result
