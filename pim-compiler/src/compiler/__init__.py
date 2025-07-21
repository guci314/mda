"""PIM Compiler - Platform Independent Model Compiler

This package provides a compiler for transforming PIM (Platform Independent Model)
files into PSM (Platform Specific Model) files and generating code using Gemini CLI.
"""

__version__ = "3.0.0"
__author__ = "PIM Compiler Team"

from .config import CompilerConfig
from .compiler_factory import CompilerFactory
from .core.pure_gemini_compiler import PureGeminiCompiler, CompilationResult

__all__ = [
    "CompilerConfig",
    "CompilerFactory",
    "PureGeminiCompiler",
    "CompilationResult"
]