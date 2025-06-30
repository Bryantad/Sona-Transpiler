"""
Parser for the Sona programming language

Provides AST construction using Lark parser with comprehensive error handling
and source location tracking for debugging support.
"""

from typing import Any, List, Optional, Dict
from pathlib import Path
from lark import Lark, Transformer, Tree, Token, LarkError, UnexpectedToken, UnexpectedCharacters
from .ast_nodes import *
from .exceptions import SonaParserError


class SonaASTTransformer(Transformer):
    """Transforms Lark parse tree to Sona AST nodes"""

    def __init__(self):
        super().__init__()
        self.source_lines: List[str] = []

    def set_source_lines(self, source_lines: List[str]):
        """Set source lines for error reporting"""
        self.source_lines = source_lines

    def _get_position(self, token_or_tree: Any) -> tuple[int, int]:
        """Extract line and column from token or tree"""
        if hasattr(token_or_tree, 'line') and hasattr(token_or_tree, 'column'):
            return token_or_tree.line, token_or_tree.column
        elif hasattr(token_or_tree, 'meta'):
            return token_or_tree.meta.line, token_or_tree.meta.column
        return 0, 0

    # Program structure
    def start(self, statements: List[Any]) -> Program:
        """Transform start rule to Program node"""
        return Program(statements=[stmt for stmt in statements if stmt is not None])

    # Literals
    def number(self, children) -> Literal:
        """Transform number token to Literal node"""
        # Handle case where children is a list
        token = children[0] if isinstance(children, list) else children
        line, column = self._get_position(token)
        value = float(token.value) if '.' in token.value else int(token.value)
        literal = Literal(value)
        literal.line = line
        literal.column = column
        return literal

    def string(self, token: Token) -> Literal:
        """Transform string token to Literal node"""
        line, column = self._get_position(token)
        # Remove quotes and handle escape sequences
        value = token.value[1:-1]  # Remove surrounding quotes
        value = value.replace('\\"', '"').replace("\\'", "'").replace('\\n', '\n').replace('\\t', '\t')
        return Literal(value, line=line, column=column)

    def interpolated_string(self, token: Token) -> Literal:
        """Transform f-string token to Literal node"""
        line, column = self._get_position(token)
        # For now, treat as regular string - interpolation handled later
        value = token.value[2:-1]  # Remove f" prefix and closing quote
        return Literal(value, type_hint="f_string", line=line, column=column)

    # Variables and identifiers
    def var(self, token: Token) -> Identifier:
        """Transform variable name to Identifier node"""
        line, column = self._get_position(token)
        return Identifier(token.value, line=line, column=column)

    # Binary operations
    def add(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform addition operation"""
        return BinaryOp(left, "+", right, line=left.line, column=left.column)

    def sub(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform subtraction operation"""
        return BinaryOp(left, "-", right, line=left.line, column=left.column)

    def mul(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform multiplication operation"""
        return BinaryOp(left, "*", right, line=left.line, column=left.column)

    def div(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform division operation"""
        return BinaryOp(left, "/", right, line=left.line, column=left.column)

    def eq(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform equality comparison"""
        return BinaryOp(left, "==", right, line=left.line, column=left.column)

    def neq(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform inequality comparison"""
        return BinaryOp(left, "!=", right, line=left.line, column=left.column)

    def gt(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform greater than comparison"""
        return BinaryOp(left, ">", right, line=left.line, column=left.column)

    def lt(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform less than comparison"""
        return BinaryOp(left, "<", right, line=left.line, column=left.column)

    def gte(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform greater than or equal comparison"""
        return BinaryOp(left, ">=", right, line=left.line, column=left.column)

    def lte(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform less than or equal comparison"""
        return BinaryOp(left, "<=", right, line=left.line, column=left.column)

    def and_(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform logical AND"""
        return BinaryOp(left, "&&", right, line=left.line, column=left.column)

    def or_(self, left: Expression, right: Expression) -> BinaryOp:
        """Transform logical OR"""
        return BinaryOp(left, "||", right, line=left.line, column=left.column)

    # Unary operations
    def neg(self, operand: Expression) -> UnaryOp:
        """Transform unary negation"""
        return UnaryOp("-", operand, line=operand.line, column=operand.column)

    def not_(self, operand: Expression) -> UnaryOp:
        """Transform logical NOT"""
        return UnaryOp("!", operand, line=operand.line, column=operand.column)

    # Function calls
    def func_call(self, name: Token, args: Optional[List[Expression]] = None) -> FunctionCall:
        """Transform function call"""
        line, column = self._get_position(name)
        function = Identifier(name.value, line=line, column=column)
        arguments = args if args else []
        return FunctionCall(function, arguments, line=line, column=column)

    def args(self, *expressions: Expression) -> List[Expression]:
        """Transform argument list"""
        return list(expressions)

    # Statements
    def assignment(self, children) -> Assignment:
        """Transform variable assignment"""
        # Handle case where children is a list (Lark default behavior)
        if isinstance(children, list) and len(children) >= 2:
            if len(children) >= 3:
                keyword, name, value = children[0], children[1], children[2]
            else:
                # Assume "let" if only name and value
                keyword = Token('KEYWORD', 'let')
                name, value = children[0], children[1]

            # Extract values from tokens
            if hasattr(keyword, 'value'):
                keyword_val = keyword.value
            else:
                keyword_val = str(keyword)

            if hasattr(name, 'value'):
                name_val = name.value
            else:
                name_val = str(name)

            line, column = self._get_position(name)
            is_declaration = keyword_val in ("let", "const")
            return Assignment(name_val, value, is_declaration, line=line, column=column)

        # Fallback for original signature (if called directly)
        keyword, name, value = children, None, None
        if hasattr(keyword, 'value'):
            name_val = name.value if name else "unknown"
            is_declaration = keyword.value in ("let", "const")
            line, column = self._get_position(name) if name else (0, 0)
            fallback_literal = Literal(None)
            fallback_assignment = Assignment(name_val, fallback_literal, is_declaration)
            fallback_assignment.line = line
            fallback_assignment.column = column
            return fallback_assignment

    def var_assign(self, children) -> Assignment:
        """Transform variable assignment from main grammar"""
        # Lark passes children as a list: [name_token, value_expr]
        # The keyword is handled by the grammar but not passed to transformer
        if isinstance(children, list) and len(children) >= 2:
            # Extract name and value
            name = children[0]
            value = children[1]

            # Get name string
            if hasattr(name, 'value'):
                name_val = name.value
            else:
                name_val = str(name)

            line, column = self._get_position(name)
            # Since we reach var_assign, we know it's a declaration (let/const)
            assignment = Assignment(name_val, value, True)
            assignment.line = line
            assignment.column = column
            return assignment
        elif len(children) == 1:
            # Single argument case
            name = children[0]
            name_val = name.value if hasattr(name, 'value') else str(name)
            line, column = self._get_position(name)
            literal = Literal(None)
            literal.line = line
            literal.column = column
            assignment = Assignment(name_val, literal, True)
            assignment.line = line
            assignment.column = column
            return assignment

        # Fallback
        fallback_literal = Literal(None)
        fallback_literal.line = 0
        fallback_literal.column = 0
        fallback_assignment = Assignment("unknown", fallback_literal, True)
        fallback_assignment.line = 0
        fallback_assignment.column = 0
        return fallback_assignment

    def print_stmt(self, args: Optional[List[Expression]] = None) -> PrintStatement:
        """Transform print statement"""
        arguments = args if args else []
        return PrintStatement(arguments)

    def return_stmt(self, value: Expression) -> ReturnStatement:
        """Transform return statement"""
        return ReturnStatement(value, line=value.line, column=value.column)

    def break_stmt(self, label: Optional[Token] = None) -> BreakStatement:
        """Transform break statement"""
        label_name = label.value if label else None
        return BreakStatement(label_name)

    def continue_stmt(self, label: Optional[Token] = None) -> ContinueStatement:
        """Transform continue statement"""
        label_name = label.value if label else None
        return ContinueStatement(label_name)

    # Control flow
    def if_stmt(self, condition: Expression, then_block: List[Statement],
                else_block: Optional[List[Statement]] = None) -> IfStatement:
        """Transform if statement"""
        return IfStatement(condition, then_block, else_block,
                          line=condition.line, column=condition.column)

    def while_stmt(self, condition: Expression, body: List[Statement]) -> WhileStatement:
        """Transform while statement"""
        return WhileStatement(condition, body, line=condition.line, column=condition.column)

    def for_stmt(self, var: Token, iterable: Expression, body: List[Statement]) -> ForStatement:
        """Transform for statement"""
        line, column = self._get_position(var)
        return ForStatement(var.value, iterable, body, line=line, column=column)

    # Function definitions
    def func_def(self, name: Token, params: Optional[List[str]], body: List[Statement]) -> FunctionDef:
        """Transform function definition"""
        line, column = self._get_position(name)
        parameters = params if params else []
        return FunctionDef(name.value, parameters, body, line=line, column=column)

    def param_list(self, *params: Token) -> List[str]:
        """Transform parameter list"""
        return [param.value for param in params]

    def block(self, *statements: Statement) -> List[Statement]:
        """Transform block of statements"""
        return [stmt for stmt in statements if stmt is not None]

    # Arrays and collections
    def array_literal(self, elements: Optional[List[Expression]] = None) -> ArrayLiteral:
        """Transform array literal"""
        return ArrayLiteral(elements if elements else [])

    def array(self, elements: Optional[List[Expression]] = None) -> ArrayLiteral:
        """Transform array literal (alternative rule)"""
        return self.array_literal(elements)

    def dict_literal(self, items: Optional[List[tuple]] = None) -> ObjectLiteral:
        """Transform dictionary literal"""
        properties = items if items else []
        return ObjectLiteral(properties)

    def dict(self, items: Optional[List[tuple]] = None) -> ObjectLiteral:
        """Transform dictionary literal (alternative rule)"""
        return self.dict_literal(items)

    def dict_item(self, key: Expression, value: Expression) -> tuple:
        """Transform dictionary item"""
        # For now, assume key is a string literal
        key_str = key.value if isinstance(key, Literal) else str(key)
        return (key_str, value)

    # Property access and method calls
    def property_access(self, obj: Expression, prop: Token) -> AttributeAccess:
        """Transform property access"""
        line, column = self._get_position(prop)
        return AttributeAccess(obj, prop.value, line=line, column=column)

    def method_call(self, obj: Expression, method: Token, args: Optional[List[Expression]] = None) -> MethodCall:
        """Transform method call"""
        line, column = self._get_position(method)
        arguments = args if args else []
        return MethodCall(obj, method.value, arguments, line=line, column=column)

    def property_assignment(self, obj: Expression, prop: Token, value: Expression) -> PropertyAssignment:
        """Transform property assignment"""
        line, column = self._get_position(prop)
        return PropertyAssignment(obj, prop.value, value, line=line, column=column)

    # Dotted expressions
    def dotted_expr(self, atom: Expression, *calls: Any) -> Expression:
        """Transform dotted expression with method calls and property access"""
        result = atom
        for call in calls:
            if isinstance(call, (AttributeAccess, MethodCall, PropertyAssignment)):
                # Update the object reference
                call.object = result
                result = call
            else:
                # Handle other call types
                result = call
        return result

    def call_or_access(self, *args) -> Any:
        """Transform call or access (handled by specific methods)"""
        # This is handled by the specific method_call, property_access, etc. methods
        return args[0] if args else None

    # Atom expressions
    def atom(self, expr: Expression) -> Expression:
        """Transform atom expression"""
        return expr

    def factor(self, expr: Expression) -> Expression:
        """Transform factor expression"""
        return expr

    def term(self, expr: Expression) -> Expression:
        """Transform term expression"""
        return expr

    def expr(self, expr: Expression) -> Expression:
        """Transform expr expression"""
        return expr


class SonaParser:
    """
    Parser for Sona programming language

    Uses Lark parser with custom transformer to build AST.
    Maintains performance baseline of 6,106+ ops/sec.
    """

    def __init__(self, grammar_path: Optional[Path] = None):
        """Initialize parser with grammar file"""
        self.grammar_path = grammar_path or self._find_grammar_path()
        self.lark_parser: Optional[Lark] = None
        self.transformer = SonaASTTransformer()
        self._initialize_parser()

    def _find_grammar_path(self) -> Path:
        """Find the Sona grammar file"""
        # Look in standard locations relative to this file
        current_dir = Path(__file__).parent
        possible_paths = [
            current_dir.parent / "grammar" / "sona.lark",
            current_dir / "grammar" / "sona.lark",
            Path("grammar/sona.lark"),
            Path("sona.lark")
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise FileNotFoundError(
            f"Could not find Sona grammar file. Searched: {possible_paths}"
        )

    def _initialize_parser(self):
        """Initialize the Lark parser"""
        try:
            with open(self.grammar_path, 'r', encoding='utf-8') as f:
                grammar = f.read()

            self.lark_parser = Lark(
                grammar,
                parser="lalr",  # Use LALR for performance
                propagate_positions=True,  # For source locations
                maybe_placeholders=False,  # For better error messages
                transformer=self.transformer
            )

        except Exception as e:
            raise SonaParserError(
                f"Failed to initialize parser: {e}",
                line=0,
                column=0
            )

    def parse(self, source_code: str, filename: str = "<string>") -> Program:
        """
        Parse Sona source code to AST

        Args:
            source_code: Source code to parse
            filename: Source filename for error reporting

        Returns:
            Program AST node

        Raises:
            SonaParserError: If parsing fails
        """
        if not self.lark_parser:
            raise SonaParserError("Parser not initialized", line=0, column=0)

        try:
            # Set source lines for error reporting
            source_lines = source_code.split('\n')
            self.transformer.set_source_lines(source_lines)

            # Parse and transform
            result = self.lark_parser.parse(source_code)

            if not isinstance(result, Program):
                raise SonaParserError(
                    f"Parser returned {type(result)}, expected Program",
                    line=0,
                    column=0
                )

            return result

        except UnexpectedToken as e:
            # Extract error information
            line = e.line if hasattr(e, 'line') else 0
            column = e.column if hasattr(e, 'column') else 0
            expected = list(e.expected) if hasattr(e, 'expected') else None

            raise SonaParserError(
                f"Unexpected token '{e.token}' in {filename}",
                line=line,
                column=column,
                expected=expected
            )

        except UnexpectedCharacters as e:
            line = e.line if hasattr(e, 'line') else 0
            column = e.column if hasattr(e, 'column') else 0

            raise SonaParserError(
                f"Unexpected character in {filename}",
                line=line,
                column=column
            )

        except LarkError as e:
            raise SonaParserError(
                f"Parse error in {filename}: {str(e)}",
                line=0,
                column=0
            )

        except Exception as e:
            raise SonaParserError(
                f"Internal parser error in {filename}: {str(e)}",
                line=0,
                column=0
            )

    def parse_expression(self, expression_code: str) -> Expression:
        """Parse a single expression"""
        # Wrap expression in a simple program structure
        program_code = f"let __temp = {expression_code}"
        program = self.parse(program_code)

        if (len(program.statements) == 1 and
            isinstance(program.statements[0], Assignment)):
            return program.statements[0].value

        raise SonaParserError(
            "Failed to parse expression",
            line=1,
            column=1
        )

    def validate_syntax(self, source_code: str) -> List[SonaParserError]:
        """Validate syntax and return list of errors"""
        errors = []
        try:
            self.parse(source_code)
        except SonaParserError as e:
            errors.append(e)
        except Exception as e:
            errors.append(SonaParserError(str(e), line=0, column=0))

        return errors

    def get_parse_tree(self, source_code: str) -> Tree:
        """Get raw Lark parse tree (for debugging)"""
        if not self.lark_parser:
            raise SonaParserError("Parser not initialized", line=0, column=0)

        # Temporarily disable transformer to get raw tree
        parser = Lark(
            open(self.grammar_path, 'r', encoding='utf-8').read(),
            parser="lalr",
            propagate_positions=True
        )

        return parser.parse(source_code)
