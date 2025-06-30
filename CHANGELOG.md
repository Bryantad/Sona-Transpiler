Changelog

All notable changes to the Sona Transpiler are documented in this file.

The format is based on Keep a Changelog and follows Semantic Versioning.

Unreleased

Planned

Enhanced error messages with syntax highlighting

Watch mode for live transpilation

Plugin system for custom transformations

Performance profiling tools

VS Code extension integration

Advanced debugging features



---

0.7.1 - 2025-06-30

🎉 Added

End-to-end Sona → Python transpilation (parser → AST → codegen)

High‑performance parsing powered by Lark (0.0000–0.0020s per file)

Source‑map support for debugging and error reporting

Hierarchical scoping and environment model

Comprehensive exception and error‑context tracking


🚀 Core Features

Variable declarations (let, const) → Python assignments

Number literals (int, float) and primitive types

Functions (default params, closures) and control flow

Data structures: lists, dicts, classes, inheritance

Import system and built‑in runtime bridge


🔧 Changed

Lark transformer signatures updated to accept list arguments [#42]

AST node constructors enhanced with line/column metadata [#45]


✅ Fixed

Environment hierarchy and variable scoping issues

Error propagation within nested AST nodes

CLI commands: run, transpile, repl, --version now stable


📊 Performance

> 6,100 transpilation ops/sec baseline



Optimized memory usage via efficient AST representation

Fast startup with lazy module loading

Minimal Python codegen overhead


🛠 Technical Specs

Python: 3.8+

Lark: >=1.1.0

Grammar rules: 178 complete Sona language rules

CLI & API: sona-transpiler on PyPI