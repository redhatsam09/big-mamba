# Big Mamba Programming Language

[![Test Big Mamba](https://github.com/redhatsam09/big-mamba/actions/workflows/test.yml/badge.svg)](https://github.com/redhatsam09/big-mamba/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/redhatsam09/big-mamba/blob/main/LICENSE)

**Python, but faster to type.**

Big Mamba shortens Python the same way Python shortened C++. It transpiles to Python under the hood.

The `.mamba` file extension is exclusive to Big Mamba. No other language uses it.

```
Python                              Big Mamba
------                              ---------
def fibonacci(n):                   fn fibonacci(n):
    if n <= 1:                          ? n <= 1:
        return n                            ret n
    return fib(n-1) + fib(n-2)         ret fib(n-1) + fib(n-2)

for i in range(10):                 @ i in rng(10):
    print(f"fib({i}) = {fib(i)}")       say $"fib({i}) = {fib(i)}"
```

---

## Installation

### pip install (Recommended)

```bash
pip install big-mamba-lang
```

After installation, use the `mamba` command from anywhere:

```bash
mamba run hello.mamba
mamba repl
mamba version
```

### Install from source

```bash
git clone https://github.com/redhatsam09/big-mamba.git
cd big-mamba
pip install .
```

### Run without installing

```bash
git clone https://github.com/redhatsam09/big-mamba.git
cd big-mamba
python mamba.py run examples/hello.mamba
python mamba.py repl
```

No external dependencies. Pure Python 3.9+.

---

## Quick Start

```bash
mamba run examples/hello.mamba        # Run a program
mamba repl                            # Interactive mode
mamba transpile examples/hello.mamba  # See generated Python
mamba tokens examples/hello.mamba     # See lexer tokens
mamba help                            # All commands
mamba version                         # Version info
```

---

## Language Reference

### Variables and Types

```
name = "Big Mamba"
age = 1
pi = 3.14
active = T
nothing = N
```

### Print and Input

```
say "Hello, World!"
say $"Hello {name}"
name = ask "What's your name? "
```

### Control Flow

```
? x > 0:
    say "positive"
?? x == 0:
    say "zero"
!:
    say "negative"

@ item in items:
    say item

@ i in rng(10):
    say i

wl running:
    process()
```

### Functions

```
fn greet(name):
    say $"Hello {name}!"
    ret $"Hi {name}"

double = lm x: x * 2
```

### Classes

```
cls Dog(Animal):
    fn init(me, name):
        me.name = name

    fn bark(me):
        say "Woof!"
```

### Special Operators

```
x++                         x += 1
x--                         x -= 1
a <> b                      a, b = b, a
result = value ?? "default" value if value is not None else "default"
$"Hello {name}"             f"Hello {name}"
```

### Imports

```
use os                      import os
use os -> path              from os import path
use numpy => np             import numpy as np
use os -> path, getcwd      from os import path, getcwd
```

### Error Handling

```
try:
    risky()
catch ValueError as e:
    say $"Error: {e}"
fin:
    cleanup()

throw ValueError("oops")
chk x > 0
```

### Comprehensions

```
squares = [x**2 @ x in rng(10)]
evens = [x @ x in rng(20) ? x % 2 == 0]
```

### Built-in Function Reference

| Big Mamba | Python        | Big Mamba | Python        |
|-----------|---------------|-----------|---------------|
| say x     | print(x)      | l(x)      | len(x)        |
| ask "?"   | input("?")    | rng(n)    | range(n)      |
| i(x)      | int(x)        | s(x)      | str(x)        |
| fl(x)     | float(x)      | ls(x)     | list(x)       |
| dt()      | dict()        | tp(x)     | tuple(x)      |
| st(x)     | set(x)        | bl(x)     | bool(x)       |
| srt(x)    | sorted(x)     | rev(x)    | reversed(x)   |
| mx(x)     | max(x)        | mn(x)     | min(x)        |
| sm(x)     | sum(x)        | ab(x)     | abs(x)        |
| enum(x)   | enumerate(x)  | zp(a,b)   | zip(a,b)      |
| mp(f,x)   | map(f,x)      | flt(f,x)  | filter(f,x)   |

### Method Reference

| Big Mamba   | Python          | Big Mamba    | Python          |
|-------------|-----------------|--------------|-----------------|
| .add(x)     | .append(x)      | .rm(x)       | .remove(x)      |
| .up()       | .upper()        | .lo()        | .lower()        |
| .trim()     | .strip()        | .spl(x)      | .split(x)       |
| .jn(x)      | .join(x)        | .rep(a,b)    | .replace(a,b)   |
| .starts(x)  | .startswith(x)  | .ends(x)     | .endswith(x)    |
| .ks()       | .keys()         | .vs()        | .values()       |
| .its()      | .items()        | .addall(x)   | .extend(x)      |

### Keyword Reference

| Big Mamba | Python   | Big Mamba | Python   |
|-----------|----------|-----------|----------|
| fn        | def      | ret       | return   |
| cls       | class    | me        | self     |
| init      | __init__ | lm        | lambda   |
| ?         | if       | ??        | elif     |
| !:        | else:    | @         | for      |
| wl        | while    | brk       | break    |
| cnt       | continue | ..        | pass     |
| use       | import   | throw     | raise    |
| catch     | except   | fin       | finally  |
| chk       | assert   | gl        | global   |
| yld       | yield    | rm        | del      |
| w/        | with     | T/F/N     | True/False/None |
| &&        | and      | \|\|      | or       |
| ~         | not      | //        | # (comment) |

---

## Architecture

Big Mamba is a transpiler. It converts Big Mamba source code to Python and executes it.

```
.mamba source -> Lexer -> Tokens -> Parser -> AST -> Transpiler -> Python -> Execution
```

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

---

## Comparison

| Feature       | C++                        | Python              | Big Mamba          |
|---------------|----------------------------|---------------------|--------------------|
| Hello World   | 5 lines                    | 1 line              | 1 line (shorter)   |
| Function def  | int f(int x) {             | def f(x):           | fn f(x):           |
| Print         | cout << x << endl;         | print(x)            | say x              |
| For loop      | for(int i=0;i<n;i++)       | for i in range(n):  | @ i in rng(n):     |
| Swap          | 3 lines + temp var         | a, b = b, a         | a <> b             |
| Self ref      | this->x                    | self.x              | me.x               |
| Import        | #include <x>               | import x            | use x              |
| Boolean       | bool b = true;             | b = True            | b = T              |

---

## Platform Support

| Platform | Install Command |
|----------|----------------|
| Windows  | `pip install big-mamba-lang` |
| macOS    | `pip3 install big-mamba-lang` |
| Linux    | `pip3 install big-mamba-lang` |

Works on any system with Python 3.9+. No external dependencies.

See [INSTALL.md](INSTALL.md) for detailed installation instructions for every OS.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Big Mamba -- Write Python at the speed of thought.
