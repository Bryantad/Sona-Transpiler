"""
Basic integration tests for the Sona Transpiler.
"""

import pytest
from sona import SonaToPythonTranspiler, SonaRuntime


class TestBasicIntegration:
    """Test basic end-to-end functionality."""

    def test_simple_transpilation(self):
        """Test basic transpilation works."""
        transpiler = SonaToPythonTranspiler()

        # Simple variable assignment
        sona_code = "let x = 42"
        python_code = transpiler.transpile(sona_code)

        assert python_code is not None
        assert len(python_code.strip()) > 0

    def test_runtime_initialization(self):
        """Test runtime can be initialized."""
        runtime = SonaRuntime()
        assert runtime is not None

    def test_package_imports(self):
        """Test that all main components can be imported."""
        from sona import (
            SonaToPythonTranspiler,
            SonaRuntime,
            SonaLexer,
            SonaParser,
            Environment,
            SourceMapper,
            main
        )

        # Test that classes can be instantiated
        transpiler = SonaToPythonTranspiler()
        runtime = SonaRuntime()
        lexer = SonaLexer()
        parser = SonaParser()
        env = Environment()
        source_mapper = SourceMapper()

        assert all([
            transpiler is not None,
            runtime is not None,
            lexer is not None,
            parser is not None,
            env is not None,
            source_mapper is not None,
            main is not None
        ])

    def test_version_available(self):
        """Test that version information is available."""
        import sona
        assert hasattr(sona, '__version__')
        assert sona.__version__ == "0.7.1"
