"""
AST Node definitions for the Sona programming language

Defines the complete Abstract Syntax Tree hierarchy with visitor pattern
support for efficient traversal during transpilation.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass


class ASTNode(ABC):
    """Base class for all AST nodes"""

    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        self.parent: Optional['ASTNode'] = None
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept a visitor for traversal"""
        pass

    def set_parent(self, parent: 'ASTNode'):
        """Set parent node"""
        self.parent = parent

    def get_source_location(self) -> str:
        """Get source location string"""
        return f"line {self.line}, column {self.column}"


class ASTVisitor(ABC):
    """Base visitor class for AST traversal"""

    @abstractmethod
    def visit_program(self, node: 'Program') -> Any:
        pass

    @abstractmethod
    def visit_assignment(self, node: 'Assignment') -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: 'Identifier') -> Any:
        pass

    @abstractmethod
    def visit_literal(self, node: 'Literal') -> Any:
        pass

    @abstractmethod
    def visit_binary_op(self, node: 'BinaryOp') -> Any:
        pass

    @abstractmethod
    def visit_unary_op(self, node: 'UnaryOp') -> Any:
        pass

    @abstractmethod
    def visit_function_call(self, node: 'FunctionCall') -> Any:
        pass

    @abstractmethod
    def visit_function_def(self, node: 'FunctionDef') -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, node: 'IfStatement') -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, node: 'WhileStatement') -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, node: 'ReturnStatement') -> Any:
        pass

    @abstractmethod
    def visit_print_stmt(self, node: 'PrintStatement') -> Any:
        pass


# Expression nodes
class Expression(ASTNode):
    """Base class for all expressions"""
    pass


@dataclass
class Literal(Expression):
    """Literal value (number, string, boolean, null)"""
    value: Union[int, float, str, bool, None]
    type_hint: Optional[str] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_literal(self)

    def __str__(self) -> str:
        return f"Literal({self.value})"


@dataclass
class Identifier(Expression):
    """Variable or function identifier"""
    name: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_identifier(self)

    def __str__(self) -> str:
        return f"Identifier({self.name})"


@dataclass
class BinaryOp(Expression):
    """Binary operation (a + b, a == b, etc.)"""
    left: Expression
    operator: str
    right: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_op(self)

    def __str__(self) -> str:
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(Expression):
    """Unary operation (-a, !a, etc.)"""
    operator: str
    operand: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_op(self)

    def __str__(self) -> str:
        return f"UnaryOp({self.operator}{self.operand})"


@dataclass
class FunctionCall(Expression):
    """Function call expression"""
    function: Expression
    arguments: List[Expression]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_call(self)

    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"FunctionCall({self.function}({args_str}))"


@dataclass
class ArrayLiteral(Expression):
    """Array literal [1, 2, 3]"""
    elements: List[Expression]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_array_literal(self)

    def __str__(self) -> str:
        elements_str = ", ".join(str(elem) for elem in self.elements)
        return f"ArrayLiteral([{elements_str}])"


@dataclass
class ObjectLiteral(Expression):
    """Object literal {key: value}"""
    properties: List[tuple[str, Expression]]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_object_literal(self)

    def __str__(self) -> str:
        props_str = ", ".join(f"{k}: {v}" for k, v in self.properties)
        return f"ObjectLiteral({{{props_str}}})"


@dataclass
class PropertyAccess(Expression):
    """Property access (obj.prop)"""
    object: Expression
    property: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_property_access(self)

    def __str__(self) -> str:
        return f"PropertyAccess({self.object}.{self.property})"


# Statement nodes
class Statement(ASTNode):
    """Base class for all statements"""
    pass


@dataclass
class Assignment(Statement):
    """Variable assignment (let x = 5)"""
    target: str
    value: Expression
    is_declaration: bool = True

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_assignment(self)

    def __str__(self) -> str:
        keyword = "let" if self.is_declaration else ""
        return f"Assignment({keyword} {self.target} = {self.value})"


@dataclass
class ExpressionStatement(Statement):
    """Expression used as statement"""
    expression: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_expression_stmt(self)

    def __str__(self) -> str:
        return f"ExpressionStatement({self.expression})"


@dataclass
class PrintStatement(Statement):
    """Print statement"""
    arguments: List[Expression]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_print_stmt(self)

    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"PrintStatement({args_str})"


@dataclass
class IfStatement(Statement):
    """If statement with optional else clause"""
    condition: Expression
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_stmt(self)

    def __str__(self) -> str:
        else_str = f" else {self.else_branch}" if self.else_branch else ""
        return f"IfStatement(if {self.condition} then {self.then_branch}{else_str})"


@dataclass
class WhileStatement(Statement):
    """While loop statement"""
    condition: Expression
    body: List[Statement]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_while_stmt(self)

    def __str__(self) -> str:
        return f"WhileStatement(while {self.condition} {self.body})"


@dataclass
class ForStatement(Statement):
    """For loop statement"""
    variable: str
    iterable: Expression
    body: List[Statement]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_for_stmt(self)

    def __str__(self) -> str:
        return f"ForStatement(for {self.variable} in {self.iterable} {self.body})"


@dataclass
class FunctionDef(Statement):
    """Function definition"""
    name: str
    parameters: List[str]
    body: List[Statement]
    return_type: Optional[str] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_def(self)

    def __str__(self) -> str:
        params_str = ", ".join(self.parameters)
        return_str = f" -> {self.return_type}" if self.return_type else ""
        return f"FunctionDef(func {self.name}({params_str}){return_str} {self.body})"


@dataclass
class ReturnStatement(Statement):
    """Return statement"""
    value: Optional[Expression] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_return_stmt(self)

    def __str__(self) -> str:
        value_str = f" {self.value}" if self.value else ""
        return f"ReturnStatement(return{value_str})"


@dataclass
class BreakStatement(Statement):
    """Break statement"""

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_break_stmt(self)

    def __str__(self) -> str:
        return "BreakStatement(break)"


@dataclass
class ContinueStatement(Statement):
    """Continue statement"""

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_continue_stmt(self)

    def __str__(self) -> str:
        return "ContinueStatement(continue)"


@dataclass
class ImportStatement(Statement):
    """Import statement"""
    module: str
    alias: Optional[str] = None
    items: Optional[List[str]] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_import_stmt(self)

    def __str__(self) -> str:
        if self.items:
            items_str = ", ".join(self.items)
            return f"ImportStatement(from {self.module} import {items_str})"
        else:
            alias_str = f" as {self.alias}" if self.alias else ""
            return f"ImportStatement(import {self.module}{alias_str})"


# Root node
@dataclass
class Program(ASTNode):
    """Root node representing the entire program"""
    statements: List[Statement]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_program(self)

    def __str__(self) -> str:
        statements_str = "\n".join(str(stmt) for stmt in self.statements)
        return f"Program(\n{statements_str}\n)"


# Utility functions for AST manipulation
def traverse_ast(node: ASTNode, visitor: ASTVisitor) -> Any:
    """Traverse AST using visitor pattern"""
    return node.accept(visitor)


def find_nodes_by_type(root: ASTNode, node_type: type) -> List[ASTNode]:
    """Find all nodes of specific type in AST"""
    nodes = []

    def collect_visitor(node):
        if isinstance(node, node_type):
            nodes.append(node)

        # Recursively visit children
        for attr_name in dir(node):
            attr_value = getattr(node, attr_name)
            if isinstance(attr_value, ASTNode):
                collect_visitor(attr_value)
            elif isinstance(attr_value, list):
                for item in attr_value:
                    if isinstance(item, ASTNode):
                        collect_visitor(item)

    collect_visitor(root)
    return nodes


def get_node_depth(node: ASTNode) -> int:
    """Get the depth of a node in the AST"""
    depth = 0
    current = node.parent
    while current:
        depth += 1
        current = current.parent
    return depth
