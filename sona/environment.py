"""
Environment and scoping system for Sona transpiler

Provides hierarchical environment management with proper lexical scoping
and variable resolution for the transpilation process.
"""

from typing import Any, Dict, List, Optional, Set, Union
from .exceptions import SonaEnvironmentError


class Environment:
    """
    Hierarchical environment for lexical scoping

    Manages variable bindings and scope resolution during transpilation.
    Supports deferred variable resolution for forward references.
    """

    def __init__(self, parent: Optional['Environment'] = None, name: str = ""):
        """
        Initialize environment

        Args:
            parent: Parent environment for scope chain
            name: Name for debugging (e.g., "global", "function", "block")
        """
        self.parent = parent
        self.name = name
        self.bindings: Dict[str, Any] = {}
        self.deferred_variables: Dict[str, List[str]] = {}
        self.scope_level = 0 if parent is None else parent.scope_level + 1
        self.is_function_scope = False
        self.is_class_scope = False

        # Track variable types for optimization
        self.variable_types: Dict[str, str] = {}
        self.constants: Set[str] = set()
        self.modified_variables: Set[str] = set()

    def define(self, name: str, value: Any, is_constant: bool = False,
               var_type: Optional[str] = None) -> None:
        """
        Define variable in current scope

        Args:
            name: Variable name
            value: Variable value
            is_constant: Whether variable is constant
            var_type: Optional type hint

        Raises:
            SonaEnvironmentError: If variable already defined in current scope
        """
        if name in self.bindings:
            raise SonaEnvironmentError(
                f"Variable '{name}' already defined in current scope",
                variable_name=name,
                scope_level=self.scope_level
            )

        self.bindings[name] = value

        if is_constant:
            self.constants.add(name)

        if var_type:
            self.variable_types[name] = var_type

    def assign(self, name: str, value: Any) -> None:
        """
        Assign value to existing variable

        Args:
            name: Variable name
            value: New value

        Raises:
            SonaEnvironmentError: If variable not found or is constant
        """
        env = self._find_defining_environment(name)
        if env is None:
            raise SonaEnvironmentError(
                f"Variable '{name}' not defined",
                variable_name=name,
                scope_level=self.scope_level
            )

        if name in env.constants:
            raise SonaEnvironmentError(
                f"Cannot assign to constant '{name}'",
                variable_name=name,
                scope_level=self.scope_level
            )

        env.bindings[name] = value
        env.modified_variables.add(name)

    def resolve(self, name: str) -> Any:
        """
        Resolve variable value

        Args:
            name: Variable name

        Returns:
            Variable value

        Raises:
            SonaEnvironmentError: If variable not found
        """
        env = self._find_defining_environment(name)
        if env is None:
            # Check if it's a deferred variable
            if self._is_deferred_variable(name):
                return DeferredVariable(name, self)

            raise SonaEnvironmentError(
                f"Variable '{name}' not defined",
                variable_name=name,
                scope_level=self.scope_level
            )

        return env.bindings[name]

    def is_defined(self, name: str) -> bool:
        """Check if variable is defined in scope chain"""
        return self._find_defining_environment(name) is not None

    def is_constant(self, name: str) -> bool:
        """Check if variable is constant"""
        env = self._find_defining_environment(name)
        return env is not None and name in env.constants

    def get_variable_type(self, name: str) -> Optional[str]:
        """Get variable type hint"""
        env = self._find_defining_environment(name)
        if env:
            return env.variable_types.get(name)
        return None

    def _find_defining_environment(self, name: str) -> Optional['Environment']:
        """Find environment where variable is defined"""
        if name in self.bindings:
            return self

        if self.parent:
            return self.parent._find_defining_environment(name)

        return None

    def _is_deferred_variable(self, name: str) -> bool:
        """Check if variable is in deferred list"""
        return name in self.deferred_variables

    def add_deferred_variable(self, name: str, reference_location: str) -> None:
        """Add deferred variable for forward reference"""
        if name not in self.deferred_variables:
            self.deferred_variables[name] = []
        self.deferred_variables[name].append(reference_location)

    def resolve_deferred_variables(self) -> List[str]:
        """Resolve deferred variables and return unresolved ones"""
        unresolved = []

        for name, locations in self.deferred_variables.items():
            if not self.is_defined(name):
                unresolved.append(f"Variable '{name}' referenced at {locations} but never defined")

        return unresolved

    def create_child_environment(self, name: str = "") -> 'Environment':
        """Create child environment"""
        child = Environment(parent=self, name=name)
        return child

    def create_function_environment(self, name: str = "function") -> 'Environment':
        """Create function scope environment"""
        env = self.create_child_environment(name)
        env.is_function_scope = True
        return env

    def create_class_environment(self, name: str = "class") -> 'Environment':
        """Create class scope environment"""
        env = self.create_child_environment(name)
        env.is_class_scope = True
        return env

    def get_all_variables(self) -> Dict[str, Any]:
        """Get all variables in current scope (for debugging)"""
        return self.bindings.copy()

    def get_scope_chain(self) -> List[str]:
        """Get scope chain for debugging"""
        chain = []
        current = self
        while current:
            chain.append(current.name or f"scope_{current.scope_level}")
            current = current.parent
        return list(reversed(chain))

    def __str__(self) -> str:
        scope_chain = " -> ".join(self.get_scope_chain())
        return f"Environment({scope_chain}): {len(self.bindings)} variables"


class DeferredVariable:
    """
    Represents a variable that will be resolved later

    Used for forward references in function definitions and class methods.
    """

    def __init__(self, name: str, environment: Environment):
        self.name = name
        self.environment = environment
        self.resolution_attempts = 0
        self.max_attempts = 3

    def resolve(self) -> Any:
        """Attempt to resolve the deferred variable"""
        self.resolution_attempts += 1

        if self.resolution_attempts > self.max_attempts:
            raise SonaEnvironmentError(
                f"Failed to resolve deferred variable '{self.name}' after {self.max_attempts} attempts",
                variable_name=self.name
            )

        try:
            return self.environment.resolve(self.name)
        except SonaEnvironmentError:
            if self.resolution_attempts >= self.max_attempts:
                raise
            # Return self for another attempt later
            return self

    def __str__(self) -> str:
        return f"DeferredVariable({self.name})"


class GlobalEnvironment(Environment):
    """
    Global environment with built-in functions and constants

    Provides the root environment with Sona's built-in functions,
    constants, and standard library imports.
    """

    def __init__(self):
        super().__init__(name="global")
        self._setup_builtins()

    def _setup_builtins(self):
        """Setup built-in functions and constants"""
        # Built-in functions
        self.define("print", BuiltinFunction("print"), is_constant=True)
        self.define("len", BuiltinFunction("len"), is_constant=True)
        self.define("str", BuiltinFunction("str"), is_constant=True)
        self.define("int", BuiltinFunction("int"), is_constant=True)
        self.define("float", BuiltinFunction("float"), is_constant=True)
        self.define("bool", BuiltinFunction("bool"), is_constant=True)
        self.define("type", BuiltinFunction("type"), is_constant=True)

        # Built-in constants
        self.define("true", True, is_constant=True, var_type="bool")
        self.define("false", False, is_constant=True, var_type="bool")
        self.define("null", None, is_constant=True, var_type="null")

        # Math constants
        self.define("PI", 3.141592653589793, is_constant=True, var_type="float")
        self.define("E", 2.718281828459045, is_constant=True, var_type="float")


class BuiltinFunction:
    """Represents a built-in function"""

    def __init__(self, name: str):
        self.name = name
        self.is_builtin = True

    def __str__(self) -> str:
        return f"<builtin function {self.name}>"

    def __call__(self, *args, **kwargs):
        # This will be handled by the runtime system
        raise NotImplementedError("Built-in functions are handled by runtime")


class EnvironmentManager:
    """
    Manages environment stack during transpilation

    Provides convenient methods for pushing and popping environments
    during different phases of transpilation.
    """

    def __init__(self):
        self.current_environment = GlobalEnvironment()
        self.environment_stack: List[Environment] = [self.current_environment]

    def push_environment(self, name: str = "") -> Environment:
        """Push new environment onto stack"""
        new_env = self.current_environment.create_child_environment(name)
        self.environment_stack.append(new_env)
        self.current_environment = new_env
        return new_env

    def push_function_environment(self, name: str = "function") -> Environment:
        """Push function environment onto stack"""
        new_env = self.current_environment.create_function_environment(name)
        self.environment_stack.append(new_env)
        self.current_environment = new_env
        return new_env

    def push_class_environment(self, name: str = "class") -> Environment:
        """Push class environment onto stack"""
        new_env = self.current_environment.create_class_environment(name)
        self.environment_stack.append(new_env)
        self.current_environment = new_env
        return new_env

    def pop_environment(self) -> Environment:
        """Pop environment from stack"""
        if len(self.environment_stack) <= 1:
            raise SonaEnvironmentError(
                "Cannot pop global environment",
                scope_level=0
            )

        popped = self.environment_stack.pop()
        self.current_environment = self.environment_stack[-1]
        return popped

    def get_current_environment(self) -> Environment:
        """Get current environment"""
        return self.current_environment

    def get_global_environment(self) -> GlobalEnvironment:
        """Get global environment"""
        return self.environment_stack[0]

    def resolve_all_deferred_variables(self) -> List[str]:
        """Resolve deferred variables in all environments"""
        all_unresolved = []

        for env in self.environment_stack:
            unresolved = env.resolve_deferred_variables()
            all_unresolved.extend(unresolved)

        return all_unresolved

    def get_scope_info(self) -> Dict[str, Any]:
        """Get scope information for debugging"""
        return {
            "current_scope": self.current_environment.name,
            "scope_level": self.current_environment.scope_level,
            "scope_chain": self.current_environment.get_scope_chain(),
            "total_environments": len(self.environment_stack),
            "variables_in_current_scope": len(self.current_environment.bindings)
        }
