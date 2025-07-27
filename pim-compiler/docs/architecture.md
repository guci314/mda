# PIM Compiler Architecture

## 1. Frontend Parser
- Responsibilities: Lexical analysis, Syntax analysis, Semantic analysis
- Input: Source code
- Output: AST (Abstract Syntax Tree)

## 2. Intermediate Representation (IR)
- Responsibilities: Optimization, Code transformation
- Formats: Control Flow Graph, SSA form

## 3. Backend Generator
- Responsibilities: Target code generation, Register allocation
- Output: Executable binary

## Interfaces
1. Parser -> IR: AST to CFG conversion API
2. IR -> Generator: Optimized IR serialization format