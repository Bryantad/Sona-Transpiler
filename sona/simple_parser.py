"""
Simplified Sona Parser Implementation

A basic but functional parser for essential Sona language features.
"""

from typing import Any, List, Optional, Dict
from pathlib import Path
from lark import Lark, Transformer, Tree, Token, LarkError
from .ast_nodes import *
from .exceptions import SonaParserError


class SimpleSonaTransformer(Transformer):
    """Simplified transformer for core Sona features"""

    def start(self, children):
        """Transform start rule to Program node"""
        statements = [stmt for stmt in children if stmt is not None]
        return Program(statements=statements)

    def assignment(self, children):
        """Transform variable assignment (simplified grammar)"""
        print(f"Assignment children: {children}, len: {len(children)}")
        for i, child in enumerate(children):
            print(f"  Child {i}: {child} (type: {type(child)})")

        if len(children) >= 3:
            keyword, name, value = children[0], children[1], children[2]
            print(f"Keyword: {keyword}, Name: {name}, Value: {value}")
            is_declaration = str(keyword) in ("let", "const")
            assignment = Assignment(str(name), value, is_declaration)
            assignment.line = 0
            assignment.column = 0
            return assignment
        elif len(children) == 2:
            # Assume it's NAME = expr (missing keyword)
            name, value = children[0], children[1]
            print(f"Missing keyword, Name: {name}, Value: {value}")
            assignment = Assignment(str(name), value, True)
            assignment.line = 0
            assignment.column = 0
            return assignment

        print("Fallback to unknown assignment")
        assignment = Assignment("unknown", Literal(None), True)
        assignment.line = 0
        assignment.column = 0
        return assignment

    def var_assign(self, children):
        """Transform variable assignment from main grammar"""
        print(f"Var_assign children: {children}, len: {len(children)}")
        for i, child in enumerate(children):
            print(f"  Child {i}: {child} (type: {type(child)})")

        # For var_assign: ("let" | "const") NAME "=" expr
        # The transformer gets: [keyword_token, name_token, value_node]
        if len(children) >= 2:
            # The grammar transforms to var_assign, so we get name and value
            name, value = children[0], children[1]
            print(f"Name: {name}, Value: {value}")
            assignment = Assignment(str(name), value, True)  # Assume declaration
            assignment.line = 0
            assignment.column = 0
            return assignment

        print("Fallback var_assign")
        assignment = Assignment("unknown", Literal(None), True)
        assignment.line = 0
        assignment.column = 0
        return assignment

    def number(self, children):
        """Transform number literal"""
        token = children[0]
        value = float(token) if '.' in str(token) else int(token)
        return Literal(value)

    def string(self, children):
        """Transform string literal"""
        token = children[0]
        # Remove quotes and handle basic escape sequences
        value = str(token)[1:-1]  # Remove surrounding quotes
        value = value.replace('\\"', '"').replace("\\'", "'")
        return Literal(value)

    def var(self, children):
        """Transform variable reference"""
        token = children[0]
        return Identifier(str(token))

    def func_call(self, children):
        """Transform function call"""
        if len(children) >= 1:
            name = children[0]
            arguments = children[1:] if len(children) > 1 else []
            function = Identifier(str(name))
            return FunctionCall(function, arguments)
        return FunctionCall(Identifier("unknown"), [])

    def args(self, children):
        """Transform argument list"""
        return list(children)

    def print_stmt(self, children):
        """Transform print statement"""
        arguments = children if children else []
        return PrintStatement(arguments)

    def add(self, children):
        """Transform addition"""
        if len(children) >= 2:
            return BinaryOp(children[0], "+", children[1])
        return BinaryOp(Literal(0), "+", Literal(0))

    def sub(self, children):
        """Transform subtraction"""
        if len(children) >= 2:
            return BinaryOp(children[0], "-", children[1])
        return BinaryOp(Literal(0), "-", Literal(0))

    def mul(self, children):
        """Transform multiplication"""
        if len(children) >= 2:
            return BinaryOp(children[0], "*", children[1])
        return BinaryOp(Literal(0), "*", Literal(0))

    def div(self, children):
        """Transform division"""
        if len(children) >= 2:
            return BinaryOp(children[0], "/", children[1])
        return BinaryOp(Literal(0), "/", Literal(1))

    def return_stmt(self, children):
        """Transform return statement"""
        value = children[0] if children else Literal(None)
        return ReturnStatement(value)

    def func_def(self, children):
        """Transform function definition"""
        if len(children) >= 3:
            name, params, body = children[0], children[1], children[2]
            param_names = params if isinstance(params, list) else []
            body_statements = body if isinstance(body, list) else []
            return FunctionDef(str(name), param_names, body_statements)
        return FunctionDef("unknown", [], [])

    def param_list(self, children):
        """Transform parameter list"""
        return [str(param) for param in children]

    def block(self, children):
        """Transform block of statements"""
        return [stmt for stmt in children if stmt is not None]

    def if_stmt(self, children):
        """Transform if statement"""
        if len(children) >= 2:
            condition, then_block = children[0], children[1]
            else_block = children[2] if len(children) > 2 else None
            return IfStatement(condition, then_block, else_block)
        return IfStatement(Literal(True), [], None)

    def while_stmt(self, children):
        """Transform while statement"""
        if len(children) >= 2:
            condition, body = children[0], children[1]
            return WhileStatement(condition, body)
        return WhileStatement(Literal(True), [])

    def for_stmt(self, children):
        """Transform for statement"""
        if len(children) >= 3:
            var, iterable, body = children[0], children[1], children[2]
            return ForStatement(str(var), iterable, body)
        return ForStatement("i", Literal([]), [])


class SimpleSonaParser:
    """Simplified Sona parser for basic functionality"""

    def __init__(self):
        self.grammar = '''
        start: statement+

        ?statement: assignment
                  | print_stmt
                  | func_def
                  | if_stmt
                  | while_stmt
                  | for_stmt
                  | return_stmt
                  | expr

        assignment: ("let" | "const") NAME "=" expr

        print_stmt: "print" "(" [args] ")"

        func_def: "func" NAME "(" [param_list] ")" block

        if_stmt: "if" expr block ["else" block]

        while_stmt: "while" expr block

        for_stmt: "for" NAME "in" expr block

        return_stmt: "return" expr

        block: "{" statement* "}"

        param_list: NAME ("," NAME)*

        args: expr ("," expr)*

        ?expr: term
             | expr "+" term   -> add
             | expr "-" term   -> sub

        ?term: factor
             | term "*" factor -> mul
             | term "/" factor -> div

        ?factor: atom
               | "-" factor     -> neg

        ?atom: NUMBER           -> number
             | STRING           -> string
             | NAME             -> var
             | func_call
             | "(" expr ")"

        func_call: NAME "(" [args] ")"

        %import common.CNAME -> NAME
        %import common.NUMBER
        %import common.ESCAPED_STRING -> STRING
        %import common.WS
        %ignore WS
        %ignore /\\/\\/[^\\n]*/
        '''

        self.parser = Lark(
            self.grammar,
            parser="lalr",
            transformer=SimpleSonaTransformer()
        )

    def parse(self, source_code: str, filename: str = "<string>") -> Program:
        """Parse Sona source code"""
        try:
            result = self.parser.parse(source_code)
            if isinstance(result, Program):
                return result
            else:
                # Wrap single statement in Program
                return Program([result])
        except Exception as e:
            raise SonaParserError(
                f"Parse error in {filename}: {str(e)}",
                line=0,
                column=0
            )
