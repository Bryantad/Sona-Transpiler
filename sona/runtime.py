"""
Runtime bridge for Sona→Python transpiler

Provides Python runtime support for Sona-specific language features,
built-in functions, and semantic compatibility.
"""

from typing import Any, Dict, List, Optional, Callable, Union
import sys
import traceback


class SonaRuntime:
    """
    Bridge between Sona language features and Python runtime

    Provides Sona built-in functions, type conversions, and runtime
    support for features that don't have direct Python equivalents.
    """

    def __init__(self):
        """Initialize Sona runtime"""
        self.builtin_functions = self._setup_builtins()
        self.globals_dict = {}
        self.type_system = None  # v0.7.1 experimental

    def _setup_builtins(self) -> Dict[str, Callable]:
        """Setup Sona built-in functions"""
        return {
            'print': self.sona_print,
            'len': self.sona_len,
            'str': self.sona_str,
            'int': self.sona_int,
            'float': self.sona_float,
            'bool': self.sona_bool,
            'type': self.sona_type,
            'range': self.sona_range,
        }

    def call_builtin(self, name: str, args: List[Any]) -> Any:
        """
        Call Sona built-in function

        Args:
            name: Function name
            args: Function arguments

        Returns:
            Function result
        """
        if name not in self.builtin_functions:
            raise NameError(f"Built-in function '{name}' not found")

        return self.builtin_functions[name](*args)

    # Sona built-in function implementations
    def sona_print(self, *args, **kwargs) -> None:
        """Sona print function - compatible with Python print"""
        # Convert args to strings using Sona string conversion
        str_args = [self.sona_str(arg) for arg in args]
        print(*str_args, **kwargs)

    def sona_len(self, obj: Any) -> int:
        """Sona len function"""
        if hasattr(obj, '__len__'):
            return len(obj)
        elif obj is None:
            return 0
        else:
            raise TypeError(f"object of type '{type(obj).__name__}' has no len()")

    def sona_str(self, obj: Any) -> str:
        """Sona string conversion"""
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, str):
            return obj
        else:
            return str(obj)

    def sona_int(self, obj: Any) -> int:
        """Sona integer conversion"""
        if isinstance(obj, str):
            try:
                return int(obj)
            except ValueError:
                raise ValueError(f"invalid literal for int(): '{obj}'")
        elif isinstance(obj, (int, float)):
            return int(obj)
        elif isinstance(obj, bool):
            return 1 if obj else 0
        elif obj is None:
            return 0
        else:
            raise TypeError(f"int() argument must be a string or number, not '{type(obj).__name__}'")

    def sona_float(self, obj: Any) -> float:
        """Sona float conversion"""
        if isinstance(obj, str):
            try:
                return float(obj)
            except ValueError:
                raise ValueError(f"could not convert string to float: '{obj}'")
        elif isinstance(obj, (int, float)):
            return float(obj)
        elif isinstance(obj, bool):
            return 1.0 if obj else 0.0
        elif obj is None:
            return 0.0
        else:
            raise TypeError(f"float() argument must be a string or number, not '{type(obj).__name__}'")

    def sona_bool(self, obj: Any) -> bool:
        """Sona boolean conversion"""
        if obj is None:
            return False
        elif isinstance(obj, bool):
            return obj
        elif isinstance(obj, (int, float)):
            return obj != 0
        elif isinstance(obj, str):
            return len(obj) > 0
        elif hasattr(obj, '__len__'):
            return len(obj) > 0
        else:
            return True

    def sona_type(self, obj: Any) -> str:
        """Sona type function"""
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "bool"
        elif isinstance(obj, int):
            return "int"
        elif isinstance(obj, float):
            return "float"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, list):
            return "array"
        elif isinstance(obj, dict):
            return "object"
        else:
            return type(obj).__name__

    def sona_range(self, *args) -> range:
        """Sona range function"""
        return range(*args)

    def handle_string_interpolation(self, template: str, values: Dict[str, Any]) -> str:
        """
        Handle f-string interpolation

        Args:
            template: Template string with {variable} placeholders
            values: Variable values for interpolation

        Returns:
            Interpolated string
        """
        try:
            return template.format(**values)
        except KeyError as e:
            raise NameError(f"name {e} is not defined in string interpolation")
        except Exception as e:
            raise ValueError(f"string interpolation error: {e}")

    def execute_with_runtime(self, python_code: str,
                           globals_dict: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute Python code with Sona runtime support

        Args:
            python_code: Generated Python code
            globals_dict: Global variables dictionary

        Returns:
            Execution result
        """
        # Setup execution environment
        if globals_dict is None:
            globals_dict = {}

        # Add Sona built-ins to globals
        globals_dict.update(self.builtin_functions)

        # Add Sona constants
        globals_dict.update({
            'true': True,
            'false': False,
            'null': None
        })

        try:
            # Execute the code
            exec(python_code, globals_dict)
            return {"success": True, "globals": globals_dict}

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }


# Global runtime instance
_runtime = SonaRuntime()

# Export built-in functions for generated code
print = _runtime.sona_print
len = _runtime.sona_len
str = _runtime.sona_str
int = _runtime.sona_int
float = _runtime.sona_float
bool = _runtime.sona_bool
type = _runtime.sona_type
range = _runtime.sona_range

# Export constants
true = True
false = False
null = None


def execute_python_code(python_code: str,
                       globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute transpiled Python code with Sona runtime

    Args:
        python_code: Generated Python code
        globals_dict: Global variables

    Returns:
        Execution result dictionary
    """
    return _runtime.execute_with_runtime(python_code, globals_dict)


def execute_python_direct(python_code: str) -> Any:
    """
    Execute Python code directly and return result

    Args:
        python_code: Python code to execute

    Returns:
        Execution result or raises exception
    """
    result = execute_python_code(python_code)

    if not result["success"]:
        # Re-raise the original exception
        error_type = result.get("error_type", "RuntimeError")
        error_message = result.get("error", "Unknown error")

        if error_type == "NameError":
            raise NameError(error_message)
        elif error_type == "TypeError":
            raise TypeError(error_message)
        elif error_type == "ValueError":
            raise ValueError(error_message)
        else:
            raise RuntimeError(error_message)

    return result


def validate_transpiled_code(python_code: str) -> Dict[str, Any]:
    """
    Validate transpiled Python code syntax

    Args:
        python_code: Generated Python code

    Returns:
        Validation result
    """
    try:
        compile(python_code, '<transpiled>', 'exec')
        return {"valid": True, "syntax_errors": []}

    except SyntaxError as e:
        return {
            "valid": False,
            "syntax_errors": [{
                "line": e.lineno,
                "column": e.offset,
                "message": e.msg,
                "text": e.text
            }]
        }
    except Exception as e:
        return {
            "valid": False,
            "syntax_errors": [{
                "line": 0,
                "column": 0,
                "message": str(e),
                "text": ""
            }]
        }


class SonaRuntimeError(Exception):
    """Runtime error specific to Sona execution"""

    def __init__(self, message: str, sona_location: Optional[str] = None):
        self.message = message
        self.sona_location = sona_location
        super().__init__(f"{message} at {sona_location}" if sona_location else message)


def get_runtime_info() -> Dict[str, Any]:
    """Get runtime information for debugging"""
    return {
        "python_version": sys.version,
        "builtin_functions": list(_runtime.builtin_functions.keys()),
        "constants": ["true", "false", "null"],
        "runtime_version": "0.7.1"
    }
