import sys
from .lexer import tokenize
from .parser import parse
from .transpiler import Transpiler, transpile
from .executor import Executor
from .errors import MambaError
from . import __version__


BANNER = f"""
  Big Mamba v{__version__}
  The shorthand programming language.

  Type 'help' for commands, 'quit' to exit.
"""

HELP_TEXT = """
  Big Mamba REPL Commands:

    help      Show this help message
    quit      Exit the REPL
    clear     Clear the screen
    py        Show the last transpiled Python code
    syntax    Show Big Mamba syntax reference

  Quick Syntax:

    say "hello"          print("hello")
    fn greet(name):      def greet(name):
    ? x > 0:             if x > 0:
    @ i in rng(10):      for i in range(10):
    x++                  x += 1
    a <> b               a, b = b, a
"""

SYNTAX_SHEET = """
  Big Mamba Syntax Reference
  ==========================

  Control Flow:
    ? cond:          if cond:
    ?? cond:         elif cond:
    !:               else:
    @ x in y:        for x in y:
    wl cond:         while cond:
    brk / cnt        break / continue
    ..               pass

  Functions and Classes:
    fn name():       def name():
    cls Name:        class Name:
    ret value        return value
    me               self
    init             __init__
    lm x: x+1       lambda x: x+1

  Built-ins:
    say x            print(x)
    ask "?"          input("?")
    l(x)             len(x)
    rng(n)           range(n)
    i(x) / s(x)     int(x) / str(x)
    T / F / N        True / False / None

  Operators:
    && / || / ~      and / or / not
    x++ / x--        x += 1 / x -= 1
    a <> b           a, b = b, a
    $"hi {x}"        f"hi {x}"

  Imports:
    use os           import os
    use os -> path   from os import path
    use np => numpy  import numpy as np

  Error Handling:
    try: / catch E: / fin:    try: / except E: / finally:
    throw Error               raise Error
    chk cond                  assert cond
"""


class REPL:

    def __init__(self):
        self.executor = Executor()
        self.transpiler = Transpiler()
        self.last_python = ""
        from .builtins import RUNTIME_PREAMBLE
        try:
            exec(compile(RUNTIME_PREAMBLE, '<preamble>', 'exec'), self.executor.global_env)
        except Exception:
            pass

    def run(self):
        print(BANNER)
        while True:
            try:
                source = self._read_input()
                if source is None:
                    continue
                source = source.strip()
                if not source:
                    continue
                if self._handle_command(source):
                    continue
                self._execute_mamba(source)
            except KeyboardInterrupt:
                print("\n  (Use 'quit' to exit)")
            except EOFError:
                print("\n  Goodbye.")
                break

    def _read_input(self):
        try:
            line = input("mamba> ")
        except (KeyboardInterrupt, EOFError):
            raise
        stripped = line.rstrip()
        if stripped.endswith(':') and not stripped.startswith('//'):
            lines = [line]
            while True:
                try:
                    next_line = input("  ...> ")
                    if next_line.strip() == '':
                        break
                    lines.append(next_line)
                except (KeyboardInterrupt, EOFError):
                    break
            return '\n'.join(lines)
        return line

    def _handle_command(self, source):
        cmd = source.strip().lower()
        if cmd in ('quit', 'exit'):
            print("  Goodbye.")
            sys.exit(0)
        if cmd == 'help':
            print(HELP_TEXT)
            return True
        if cmd == 'clear':
            print('\033[2J\033[H')
            return True
        if cmd == 'py':
            if self.last_python:
                print("  -- Transpiled Python --")
                print(self.last_python)
                print("  -----------------------")
            else:
                print("  No code transpiled yet.")
            return True
        if cmd == 'syntax':
            print(SYNTAX_SHEET)
            return True
        return False

    def _execute_mamba(self, source):
        try:
            tokens = tokenize(source)
            ast = parse(tokens, source)
            python_code = self.transpiler.transpile(ast, include_preamble=False)
            self.last_python = python_code.strip()
            result, success = self.executor.execute_expression(python_code)
            if success:
                if result is not None:
                    print(repr(result))
            else:
                print(f"  RuntimeError: {result}")
        except MambaError as e:
            print(e)
        except Exception as e:
            print(f"  Error: {e}")


def start_repl():
    repl = REPL()
    repl.run()
