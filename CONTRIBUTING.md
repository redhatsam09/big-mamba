# Contributing to Big Mamba

Thank you for your interest in contributing to Big Mamba.

## How to Contribute

### Reporting Bugs
- Open an issue on GitHub
- Include the `.mamba` code that causes the bug
- Include the error message
- Include your Python version and OS

### Suggesting Features
- Open an issue with the title prefixed by `[Feature]`
- Describe what the feature does
- Show example Big Mamba syntax for the feature
- Explain how it maps to Python

### Submitting Code
1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test all examples: run each file in the `examples/` directory
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

### Code Standards
- No comments in source code
- No emojis in any file
- No external dependencies (pure Python 3.6+)
- All files must be clean and professional
- Test all examples before submitting

### Project Structure

```
bigmamba/
    __init__.py      Package metadata
    lexer.py         Tokenizer
    parser.py        Recursive descent parser
    ast_nodes.py     AST node definitions
    transpiler.py    AST to Python code generator
    executor.py      Python code executor
    repl.py          Interactive REPL
    builtins.py      Keyword and function mappings
    errors.py        Custom error types

examples/            Example .mamba programs
mamba.py             CLI entry point
```

### Adding a New Keyword or Shorthand
1. Add the mapping to `bigmamba/builtins.py`
2. If it is a keyword, add it to `KEYWORDS` in `bigmamba/lexer.py`
3. If it needs special parsing, update `bigmamba/parser.py`
4. If it needs special transpilation, update `bigmamba/transpiler.py`
5. Add the runtime alias to `RUNTIME_PREAMBLE` in `bigmamba/builtins.py`
6. Update `README.md` with the new syntax
7. Add an example demonstrating the feature

### Adding a New Method Shorthand
1. Add the mapping to `METHOD_MAP` in `bigmamba/builtins.py`
2. Add the mapping to `method_remap` in `bigmamba/parser.py` (in `parse_postfix`)
3. Update the Method Reference table in `README.md`

### Testing
Run all examples to verify nothing is broken:

```bash
python mamba.py run examples/hello.mamba
python mamba.py run examples/fibonacci.mamba
python mamba.py run examples/calculator.mamba
python mamba.py run examples/classes.mamba
python mamba.py run examples/guessing_game.mamba
```

Verify transpiled output is correct:

```bash
python mamba.py transpile examples/hello.mamba
```

Test the REPL:

```bash
python mamba.py repl
```
