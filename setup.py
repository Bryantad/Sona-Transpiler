"""
Sona Transpiler Setup Configuration

A focused, production-grade transpiler for the Sona programming language.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from the package
version = {}
with open("sona/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="sona-transpiler",
    version=version.get("__version__", "0.7.1"),
    author="Bryant Adams",
    author_email="your.email@example.com",  # Replace with actual email
    description="A focused, production-grade transpiler for the Sona programming language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bryantad/Sona-Transpiler",
    project_urls={
        "Bug Tracker": "https://github.com/Bryantad/Sona-Transpiler/issues",
        "Documentation": "https://github.com/Bryantad/Sona-Transpiler/wiki",
        "Source Code": "https://github.com/Bryantad/Sona-Transpiler",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lark>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sona=sona.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sona": ["../grammar/*.lark"],
    },
    keywords=[
        "sona",
        "transpiler",
        "compiler",
        "programming-language",
        "python",
        "ast",
        "parser",
    ],
    zip_safe=False,
)
