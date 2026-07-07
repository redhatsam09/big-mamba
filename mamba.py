import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bigmamba.lexer import tokenize
from bigmamba.parser import parse
from bigmamba.transpiler import transpile
from bigmamba.executor import Executor
from bigmamba.repl import start_repl
from bigmamba.errors import MambaError
from bigmamba import __version__


def print_help():
    print(f"""
  Big Mamba v{__version__}
  The shorthand programming language.

  Usage:
    mamba run <file.mamba>        Run a Big Mamba program
    mamba repl                    Start interactive REPL
    mamba transpile <file.mamba>  Show generated Python code
    mamba tokens <file.mamba>     Show lexer tokens
    mamba help                    Show this help message
    mamba version                 Show version

  Examples:
    mamba run hello.mamba
    mamba repl
    mamba transpile fibonacci.mamba

  File Extension: .mamba
""")


def read_file(filepath):
    if not os.path.exists(filepath):
        print(f"  Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    if not filepath.endswith('.mamba'):
        print(f"  Warning: File does not have .mamba extension", file=sys.stderr)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def cmd_run(filepath):
    source = read_file(filepath)
    try:
        tokens = tokenize(source, filepath)
        ast = parse(tokens, source)
        python_code = transpile(ast, include_preamble=True)
        executor = Executor()
        executor.execute(python_code, filename=filepath)
    except MambaError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        print(f"  Internal Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_transpile(filepath):
    source = read_file(filepath)
    try:
        tokens = tokenize(source, filepath)
        ast = parse(tokens, source)
        python_code = transpile(ast, include_preamble=False)
        print(f"  -- Transpiled Python from: {filepath} --")
        print()
        for i, line in enumerate(python_code.strip().split('\n'), 1):
            print(f"  {i:3d}  {line}")
        print()
        print(f"  {'─' * 45}")
    except MambaError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def cmd_tokens(filepath):
    source = read_file(filepath)
    try:
        tokens = tokenize(source, filepath)
        print(f"  -- Tokens from: {filepath} --")
        print()
        for tok in tokens:
            print(f"  L{tok.line:3d}:{tok.col:<3d}  {tok.type.name:<18s}  {repr(tok.value)}")
        print()
    except MambaError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('help', '--help', '-h'):
        print_help()
        return
    if args[0] in ('version', '--version', '-v'):
        print(f"Big Mamba v{__version__}")
        return
    command = args[0]
    if command == 'repl':
        start_repl()
    elif command == 'run':
        if len(args) < 2:
            print("  Error: Please provide a .mamba file to run", file=sys.stderr)
            print("  Usage: mamba run <file.mamba>")
            sys.exit(1)
        cmd_run(args[1])
    elif command == 'transpile':
        if len(args) < 2:
            print("  Error: Please provide a .mamba file to transpile", file=sys.stderr)
            sys.exit(1)
        cmd_transpile(args[1])
    elif command == 'tokens':
        if len(args) < 2:
            print("  Error: Please provide a .mamba file", file=sys.stderr)
            sys.exit(1)
        cmd_tokens(args[1])
    else:
        if command.endswith('.mamba') or os.path.exists(command):
            cmd_run(command)
        else:
            print(f"  Unknown command: {command}", file=sys.stderr)
            print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
