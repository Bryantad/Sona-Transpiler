"""
Source mapping for debugging support

Provides source location tracking and mapping between Sona source code
and generated Python code for debugging and error reporting.
"""

from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
import json


class SourceLocation(NamedTuple):
    """Represents a location in source code"""
    line: int
    column: int
    filename: str = "<string>"


@dataclass
class MappingEntry:
    """Single source mapping entry"""
    generated_line: int
    generated_column: int
    source_line: int
    source_column: int
    source_filename: str
    name: Optional[str] = None


class SourceMapper:
    """
    Source mapping for Sona→Python transpilation

    Tracks the relationship between Sona source locations and generated
    Python code for debugging and error reporting.
    """

    def __init__(self):
        """Initialize source mapper"""
        self.mappings: List[MappingEntry] = []
        self.source_files: Dict[str, str] = {}
        self.generated_lines: List[str] = []
        self.current_generated_line = 1
        self.current_generated_column = 0

    def add_source_file(self, filename: str, content: str) -> None:
        """Add source file content for reference"""
        self.source_files[filename] = content

    def map_location(self,
                    sona_line: int,
                    sona_column: int,
                    sona_filename: str = "<string>",
                    name: Optional[str] = None) -> None:
        """
        Map current generated position to Sona source location

        Args:
            sona_line: Line in Sona source
            sona_column: Column in Sona source
            sona_filename: Sona source filename
            name: Optional symbol name
        """
        mapping = MappingEntry(
            generated_line=self.current_generated_line,
            generated_column=self.current_generated_column,
            source_line=sona_line,
            source_column=sona_column,
            source_filename=sona_filename,
            name=name
        )

        self.mappings.append(mapping)

    def advance_generated_position(self, text: str) -> None:
        """
        Advance generated position based on emitted text

        Args:
            text: Generated Python code text
        """
        lines = text.split('\n')

        if len(lines) == 1:
            # Single line - advance column
            self.current_generated_column += len(text)
        else:
            # Multiple lines - advance line and reset column
            self.current_generated_line += len(lines) - 1
            self.current_generated_column = len(lines[-1])

        # Track generated lines for debugging
        if len(lines) > 1:
            self.generated_lines.extend(lines[:-1])
            if len(self.generated_lines) >= self.current_generated_line:
                self.generated_lines[self.current_generated_line - 1] = lines[-1]
            else:
                self.generated_lines.append(lines[-1])

    def get_sona_location(self, python_line: int, python_column: int) -> Optional[SourceLocation]:
        """
        Get Sona source location for generated Python location

        Args:
            python_line: Line in generated Python code
            python_column: Column in generated Python code

        Returns:
            Corresponding Sona source location, if found
        """
        # Find the closest mapping entry
        best_mapping = None
        best_distance = float('inf')

        for mapping in self.mappings:
            if (mapping.generated_line < python_line or
                (mapping.generated_line == python_line and
                 mapping.generated_column <= python_column)):

                # Calculate distance
                line_distance = python_line - mapping.generated_line
                column_distance = 0
                if line_distance == 0:
                    column_distance = python_column - mapping.generated_column

                total_distance = line_distance * 1000 + column_distance

                if total_distance < best_distance:
                    best_distance = total_distance
                    best_mapping = mapping

        if best_mapping:
            return SourceLocation(
                line=best_mapping.source_line,
                column=best_mapping.source_column,
                filename=best_mapping.source_filename
            )

        return None

    def get_python_location(self, sona_line: int, sona_column: int,
                           sona_filename: str = "<string>") -> Optional[Tuple[int, int]]:
        """
        Get Python location for Sona source location

        Args:
            sona_line: Line in Sona source
            sona_column: Column in Sona source
            sona_filename: Sona source filename

        Returns:
            Corresponding Python location (line, column), if found
        """
        for mapping in self.mappings:
            if (mapping.source_filename == sona_filename and
                mapping.source_line == sona_line and
                mapping.source_column == sona_column):
                return (mapping.generated_line, mapping.generated_column)

        return None

    def generate_source_map(self) -> Dict:
        """
        Generate source map in JSON format

        Returns:
            Source map dictionary compatible with debugging tools
        """
        return {
            "version": 3,
            "sources": list(self.source_files.keys()),
            "sourcesContent": [self.source_files[f] for f in self.source_files.keys()],
            "mappings": self._encode_mappings(),
            "names": self._get_all_names()
        }

    def _encode_mappings(self) -> str:
        """Encode mappings in VLQ format (simplified)"""
        # For now, return a simple representation
        # In a full implementation, this would use VLQ encoding
        encoded_mappings = []

        for mapping in self.mappings:
            encoded_mappings.append(
                f"{mapping.generated_line}:{mapping.generated_column}"
                f"->{mapping.source_line}:{mapping.source_column}"
            )

        return ";".join(encoded_mappings)

    def _get_all_names(self) -> List[str]:
        """Get all symbol names from mappings"""
        names = set()
        for mapping in self.mappings:
            if mapping.name:
                names.add(mapping.name)
        return sorted(list(names))

    def format_error_with_source(self,
                                python_line: int,
                                python_column: int,
                                error_message: str) -> str:
        """
        Format error message with Sona source context

        Args:
            python_line: Line in generated Python code where error occurred
            python_column: Column in generated Python code
            error_message: Original error message

        Returns:
            Formatted error message with Sona source context
        """
        sona_location = self.get_sona_location(python_line, python_column)

        if not sona_location:
            return f"{error_message} (at generated Python line {python_line})"

        # Get source context
        source_context = self._get_source_context(
            sona_location.filename,
            sona_location.line,
            sona_location.column
        )

        formatted_error = f"{error_message}\n"
        formatted_error += f"  at {sona_location.filename}:{sona_location.line}:{sona_location.column}\n"

        if source_context:
            formatted_error += f"\nSource context:\n{source_context}"

        return formatted_error

    def _get_source_context(self, filename: str, line: int, column: int) -> str:
        """Get source code context around error location"""
        if filename not in self.source_files:
            return ""

        source_lines = self.source_files[filename].split('\n')

        if line <= 0 or line > len(source_lines):
            return ""

        # Show 2 lines before and after error line
        context_lines = []
        start_line = max(1, line - 2)
        end_line = min(len(source_lines), line + 2)

        for i in range(start_line, end_line + 1):
            if i <= len(source_lines):
                prefix = ">>> " if i == line else "    "
                context_lines.append(f"{prefix}{i:3}: {source_lines[i-1]}")

                # Add column indicator for error line
                if i == line:
                    indicator = " " * (7 + column) + "^"
                    context_lines.append(indicator)

        return "\n".join(context_lines)

    def get_mapping_statistics(self) -> Dict:
        """Get statistics about source mappings"""
        return {
            "total_mappings": len(self.mappings),
            "source_files": len(self.source_files),
            "generated_lines": self.current_generated_line,
            "coverage": self._calculate_coverage()
        }

    def _calculate_coverage(self) -> float:
        """Calculate mapping coverage percentage"""
        if not self.mappings or self.current_generated_line == 0:
            return 0.0

        # Simple coverage calculation based on mapped lines
        mapped_lines = set(mapping.generated_line for mapping in self.mappings)
        coverage = len(mapped_lines) / self.current_generated_line
        return min(100.0, coverage * 100.0)

    def export_to_file(self, filename: str) -> None:
        """Export source map to file"""
        source_map = self.generate_source_map()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(source_map, f, indent=2)

    def reset(self) -> None:
        """Reset mapper state"""
        self.mappings.clear()
        self.source_files.clear()
        self.generated_lines.clear()
        self.current_generated_line = 1
        self.current_generated_column = 0

    def clone(self) -> 'SourceMapper':
        """Create a copy of the source mapper"""
        new_mapper = SourceMapper()
        new_mapper.mappings = self.mappings.copy()
        new_mapper.source_files = self.source_files.copy()
        new_mapper.generated_lines = self.generated_lines.copy()
        new_mapper.current_generated_line = self.current_generated_line
        new_mapper.current_generated_column = self.current_generated_column
        return new_mapper


class DebugInfo:
    """
    Debug information container

    Stores additional debugging information for transpiled code including
    variable mappings, function boundaries, and optimization information.
    """

    def __init__(self):
        """Initialize debug info"""
        self.function_boundaries: Dict[str, Tuple[int, int]] = {}
        self.variable_mappings: Dict[str, str] = {}
        self.optimization_info: List[str] = []
        self.performance_hints: List[str] = []

    def add_function_boundary(self, function_name: str, start_line: int, end_line: int):
        """Add function boundary information"""
        self.function_boundaries[function_name] = (start_line, end_line)

    def add_variable_mapping(self, sona_name: str, python_name: str):
        """Add variable name mapping"""
        self.variable_mappings[sona_name] = python_name

    def add_optimization_info(self, info: str):
        """Add optimization information"""
        self.optimization_info.append(info)

    def add_performance_hint(self, hint: str):
        """Add performance hint"""
        self.performance_hints.append(hint)

    def get_debug_summary(self) -> Dict:
        """Get debug information summary"""
        return {
            "functions": len(self.function_boundaries),
            "variable_mappings": len(self.variable_mappings),
            "optimizations": len(self.optimization_info),
            "performance_hints": len(self.performance_hints)
        }
