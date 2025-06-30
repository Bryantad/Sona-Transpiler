#!/usr/bin/env python3
"""
Sona Transpiler CLI Interface

Provides command-line access to Sona transpilation, REPL, and utility functions.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List

from .transpiler import SonaToPythonTranspiler
from .runtime import SonaRuntime
from .exceptions import SonaTranspilerError
from . import __version__


class SonaCLI:
    """Command-line interface for the Sona transpiler."""

    def __init__(self):
        self.transpiler = SonaToPythonTranspiler()
        self.runtime = SonaRuntime()

    def run_file(self, file_path: str, output_path: Optional[str] = None) -> int:
        """Run a Sona file by transpiling and executing it."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Transpile to Python
            python_code = self.transpiler.transpile(source_code, file_path)

            # Save transpiled code if output path specified
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                print(f"Transpiled code saved to: {output_path}")

            # Execute the transpiled Python code
            self.runtime.execute(python_code, file_path)
            return 0

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
            return 1
        except SonaTranspilerError as e:
            print(f"Sona Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    def transpile_file(self, file_path: str, output_path: str) -> int:
        """Transpile a Sona file to Python without executing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            python_code = self.transpiler.transpile(source_code, file_path)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_code)

            print(f"Successfully transpiled '{file_path}' to '{output_path}'")
            return 0

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
            return 1
        except SonaTranspilerError as e:
            print(f"Sona Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    def start_repl(self) -> int:
        """Start the Sona REPL (Read-Eval-Print Loop)."""
        print(f"Sona Transpiler REPL v{__version__}")
        print("Type 'exit()' or 'quit()' to exit, 'help()' for help.")
        print("-" * 50)

        while True:
            try:
                # Get input
                line = input("sona> ").strip()

                # Handle special commands
                if line in ('exit()', 'quit()', 'exit', 'quit'):
                    print("Goodbye!")
                    break
                elif line in ('help()', 'help'):
                    self._show_repl_help()
                    continue
                elif not line:
                    continue

                # Transpile and execute
                try:
                    python_code = self.transpiler.transpile(line, "<repl>")
                    result = self.runtime.execute(python_code, "<repl>")
                    if result is not None:
                        print(repr(result))
                except SonaTranspilerError as e:
                    print(f"Error: {e}")

            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")

        return 0

    def _show_repl_help(self):
        """Show REPL help information."""
        print("""
Sona REPL Help:
  - Enter Sona code to execute it immediately
  - exit() or quit() - Exit the REPL
  - help() - Show this help message

Examples:
  sona> print("Hello, World!")
  sona> let x = 42
  sona> print(x + 8)
  sona> func add(a, b) { return a + b }
  sona> print(add(5, 3))
        """)

    def show_version(self) -> int:
        """Show version information."""
        print(f"Sona Transpiler v{__version__}")
        print("A fast, focused transpiler for the Sona programming language.")
        return 0


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='sona',
        description='Sona Transpiler - Transpile and run Sona code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sona run script.sona                    # Run a Sona file
  sona transpile script.sona output.py   # Transpile to Python
  sona repl                              # Start interactive REPL
  sona --version                         # Show version info
        """
    )

    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version information'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run a Sona file')
    run_parser.add_argument('file', help='Sona file to run')
    run_parser.add_argument(
        '--output', '-o',
        help='Save transpiled Python code to file'
    )

    # Transpile command
    transpile_parser = subparsers.add_parser('transpile', help='Transpile Sona to Python')
    transpile_parser.add_argument('input', help='Input Sona file')
    transpile_parser.add_argument('output', help='Output Python file')

    # REPL command
    subparsers.add_parser('repl', help='Start interactive REPL')

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    cli = SonaCLI()

    if args.version:
        return cli.show_version()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'run':
        return cli.run_file(args.file, args.output)
    elif args.command == 'transpile':
        return cli.transpile_file(args.input, args.output)
    elif args.command == 'repl':
        return cli.start_repl()
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
