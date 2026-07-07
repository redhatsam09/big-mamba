import sys
import os
import traceback
from .errors import MambaRuntimeError

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


class Executor:

    def __init__(self):
        self.global_env = {}
        self._setup_env()

    def _setup_env(self):
        import builtins
        self.global_env = {
            '__builtins__': builtins,
            '__name__': '__main__',
        }

    def execute(self, python_code, source_map=None, filename="<mamba>"):
        try:
            compiled = compile(python_code, filename, 'exec')
            exec(compiled, self.global_env)
            return True
        except SystemExit:
            raise
        except Exception as e:
            self._handle_error(e, python_code, source_map)
            return False

    def execute_expression(self, python_code):
        try:
            compiled = compile(python_code, '<mamba-repl>', 'eval')
            result = eval(compiled, self.global_env)
            return result, True
        except SyntaxError:
            try:
                compiled = compile(python_code, '<mamba-repl>', 'exec')
                exec(compiled, self.global_env)
                return None, True
            except SystemExit:
                raise
            except Exception as e:
                return e, False
        except SystemExit:
            raise
        except Exception as e:
            return e, False

    def _handle_error(self, error, python_code, source_map=None):
        error_type = type(error).__name__
        error_msg = str(error)
        tb = traceback.extract_tb(error.__traceback__)
        line_no = None
        for frame in reversed(tb):
            if frame.filename in ('<mamba>', '<mamba-repl>', '<string>'):
                line_no = frame.lineno
                break
        source_line = None
        if line_no and python_code:
            lines = python_code.split('\n')
            if 0 < line_no <= len(lines):
                source_line = lines[line_no - 1]
        raise MambaRuntimeError(
            f"{error_type}: {error_msg}",
            line=line_no,
            source_line=source_line
        )


def execute(python_code, filename="<mamba>"):
    executor = Executor()
    return executor.execute(python_code, filename=filename)
