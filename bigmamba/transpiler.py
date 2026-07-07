import re
from .ast_nodes import *
from .builtins import BUILTIN_FUNC_MAP, RUNTIME_PREAMBLE
from .errors import MambaTranspileError


class Transpiler:

    def __init__(self):
        self.indent_level = 0
        self.output_lines = []

    def transpile(self, ast, include_preamble=True):
        self.indent_level = 0
        self.output_lines = []
        if include_preamble:
            self.output_lines.append(RUNTIME_PREAMBLE)
        if isinstance(ast, Program):
            for stmt in ast.statements:
                self._emit_statement(stmt)
        else:
            self._emit_statement(ast)
        return '\n'.join(self.output_lines)

    def _indent(self):
        return '    ' * self.indent_level

    def _emit(self, line):
        self.output_lines.append(self._indent() + line)

    def _emit_statement(self, node):
        if isinstance(node, ExpressionStatement):
            self._emit(self._expr(node.expression))
        elif isinstance(node, Assignment):
            targets_str = ' = '.join(self._expr(t) for t in node.targets)
            self._emit(f'{targets_str} = {self._expr(node.value)}')
        elif isinstance(node, AugmentedAssignment):
            self._emit(f'{self._expr(node.target)} {node.op} {self._expr(node.value)}')
        elif isinstance(node, Increment):
            self._emit(f'{self._expr(node.target)} += 1')
        elif isinstance(node, Decrement):
            self._emit(f'{self._expr(node.target)} -= 1')
        elif isinstance(node, Swap):
            l = self._expr(node.left)
            r = self._expr(node.right)
            self._emit(f'{l}, {r} = {r}, {l}')
        elif isinstance(node, Pass):
            self._emit('pass')
        elif isinstance(node, Break):
            self._emit('break')
        elif isinstance(node, Continue):
            self._emit('continue')
        elif isinstance(node, Return):
            if node.value:
                self._emit(f'return {self._expr(node.value)}')
            else:
                self._emit('return')
        elif isinstance(node, Yield):
            if node.value:
                self._emit(f'yield {self._expr(node.value)}')
            else:
                self._emit('yield')
        elif isinstance(node, Global):
            self._emit(f'global {", ".join(node.names)}')
        elif isinstance(node, Assert):
            if node.msg:
                self._emit(f'assert {self._expr(node.test)}, {self._expr(node.msg)}')
            else:
                self._emit(f'assert {self._expr(node.test)}')
        elif isinstance(node, Raise):
            if node.exception:
                self._emit(f'raise {self._expr(node.exception)}')
            else:
                self._emit('raise')
        elif isinstance(node, Delete):
            self._emit(f'del {self._expr(node.target)}')
        elif isinstance(node, Comment):
            self._emit(f'# {node.text}')
        elif isinstance(node, Docstring):
            self._emit(f'"""{node.text}"""')
        elif isinstance(node, IfStatement):
            self._emit_if(node)
        elif isinstance(node, ForLoop):
            self._emit_for(node)
        elif isinstance(node, WhileLoop):
            self._emit_while(node)
        elif isinstance(node, TryCatch):
            self._emit_try(node)
        elif isinstance(node, WithStatement):
            self._emit_with(node)
        elif isinstance(node, FunctionDef):
            self._emit_function(node)
        elif isinstance(node, ClassDef):
            self._emit_class(node)
        elif isinstance(node, Import):
            self._emit_import(node)
        elif isinstance(node, ImportFrom):
            self._emit_import_from(node)
        else:
            self._emit(self._expr(node))

    def _emit_if(self, node):
        self._emit(f'if {self._expr(node.condition)}:')
        self._emit_block(node.body)
        for cond, body in node.elif_clauses:
            self._emit(f'elif {self._expr(cond)}:')
            self._emit_block(body)
        if node.else_body:
            self._emit('else:')
            self._emit_block(node.else_body)

    def _emit_for(self, node):
        self._emit(f'for {self._expr(node.target)} in {self._expr(node.iterable)}:')
        self._emit_block(node.body)
        if node.else_body:
            self._emit('else:')
            self._emit_block(node.else_body)

    def _emit_while(self, node):
        self._emit(f'while {self._expr(node.condition)}:')
        self._emit_block(node.body)
        if node.else_body:
            self._emit('else:')
            self._emit_block(node.else_body)

    def _emit_try(self, node):
        self._emit('try:')
        self._emit_block(node.try_body)
        for exc_type, exc_name, exc_body in node.except_clauses:
            if exc_type and exc_name:
                self._emit(f'except {self._expr(exc_type)} as {exc_name}:')
            elif exc_type:
                self._emit(f'except {self._expr(exc_type)}:')
            else:
                self._emit('except:')
            self._emit_block(exc_body)
        if node.else_body:
            self._emit('else:')
            self._emit_block(node.else_body)
        if node.finally_body:
            self._emit('finally:')
            self._emit_block(node.finally_body)

    def _emit_with(self, node):
        ctx = self._expr(node.context)
        if node.name:
            self._emit(f'with {ctx} as {node.name}:')
        else:
            self._emit(f'with {ctx}:')
        self._emit_block(node.body)

    def _emit_function(self, node):
        for dec in node.decorators:
            dec_str = self._expr(dec)
            dec_remap = {
                'static': 'staticmethod',
                'clsm': 'classmethod',
                'prop': 'property',
            }
            if dec_str in dec_remap:
                dec_str = dec_remap[dec_str]
            self._emit(f'@{dec_str}')
        params = self._format_params(node.params)
        self._emit(f'def {node.name}({params}):')
        self._emit_block(node.body)

    def _emit_class(self, node):
        for dec in node.decorators:
            self._emit(f'@{self._expr(dec)}')
        bases = ', '.join(self._expr(b) for b in node.bases) if node.bases else ''
        if bases:
            self._emit(f'class {node.name}({bases}):')
        else:
            self._emit(f'class {node.name}:')
        self._emit_block(node.body)

    def _format_params(self, params):
        parts = []
        for p in params:
            s = ''
            if p.is_kwargs:
                s = '**'
            elif p.is_args:
                s = '*'
            s += p.name
            if p.default:
                s += f'={self._expr(p.default)}'
            parts.append(s)
        return ', '.join(parts)

    def _emit_import(self, node):
        if node.alias:
            self._emit(f'import {node.module} as {node.alias}')
        else:
            self._emit(f'import {node.module}')

    def _emit_import_from(self, node):
        names = ', '.join(
            f'{n} as {a}' if a else n for n, a in node.names
        )
        self._emit(f'from {node.module} import {names}')

    def _emit_block(self, statements):
        self.indent_level += 1
        if not statements:
            self._emit('pass')
        else:
            for stmt in statements:
                self._emit_statement(stmt)
        self.indent_level -= 1

    def _expr(self, node):
        if node is None:
            return 'None'
        if isinstance(node, Name):
            return self._map_name(node.name)
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, String):
            escaped = node.value.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
            return f"'{escaped}'"
        if isinstance(node, FString):
            content = node.value
            content = re.sub(r'\bme\.', 'self.', content)
            content = re.sub(r'\.init\b', '.__init__', content)
            content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            content = content.replace('"', '\\"')
            return f'f"{content}"'
        if isinstance(node, BinaryOp):
            left = self._expr(node.left)
            right = self._expr(node.right)
            return f'({left} {node.op} {right})'
        if isinstance(node, UnaryOp):
            return f'({node.op}{self._expr(node.operand)})'
        if isinstance(node, Compare):
            parts = [self._expr(node.left)]
            for op, comp in zip(node.ops, node.comparators):
                parts.append(f'{op} {self._expr(comp)}')
            return f'({" ".join(parts)})'
        if isinstance(node, BoolOp):
            parts = [self._expr(v) for v in node.values]
            return f'({f" {node.op} ".join(parts)})'
        if isinstance(node, NotOp):
            return f'(not {self._expr(node.operand)})'
        if isinstance(node, Call):
            func_name = self._expr(node.func)
            func_name = self._map_builtin_func(func_name)
            args = [self._expr(a) for a in node.args]
            kwargs = [f'{k}={self._expr(v)}' for k, v in node.kwargs]
            all_args = ', '.join(args + kwargs)
            return f'{func_name}({all_args})'
        if isinstance(node, Attribute):
            attr = node.attr
            if attr == '__init__':
                pass
            return f'{self._expr(node.obj)}.{attr}'
        if isinstance(node, Subscript):
            return f'{self._expr(node.obj)}[{self._expr(node.index)}]'
        if isinstance(node, Slice):
            lower = self._expr(node.lower) if node.lower else ''
            upper = self._expr(node.upper) if node.upper else ''
            if node.step:
                return f'{lower}:{upper}:{self._expr(node.step)}'
            return f'{lower}:{upper}'
        if isinstance(node, ListLiteral):
            elements = ', '.join(self._expr(e) for e in node.elements)
            return f'[{elements}]'
        if isinstance(node, DictLiteral):
            pairs = ', '.join(f'{self._expr(k)}: {self._expr(v)}' for k, v in node.pairs)
            return f'{{{pairs}}}'
        if isinstance(node, TupleLiteral):
            if not node.elements:
                return '()'
            elements = ', '.join(self._expr(e) for e in node.elements)
            if len(node.elements) == 1:
                return f'({elements},)'
            return f'({elements})'
        if isinstance(node, SetLiteral):
            elements = ', '.join(self._expr(e) for e in node.elements)
            return f'{{{elements}}}'
        if isinstance(node, ListComp):
            cond = f' if {self._expr(node.condition)}' if node.condition else ''
            return f'[{self._expr(node.element)} for {self._expr(node.target)} in {self._expr(node.iterable)}{cond}]'
        if isinstance(node, DictComp):
            cond = f' if {self._expr(node.condition)}' if node.condition else ''
            return f'{{{self._expr(node.key)}: {self._expr(node.value)} for {self._expr(node.target)} in {self._expr(node.iterable)}{cond}}}'
        if isinstance(node, Lambda):
            params = ', '.join(node.params)
            return f'lambda {params}: {self._expr(node.body)}'
        if isinstance(node, Ternary):
            return f'({self._expr(node.true_value)} if {self._expr(node.condition)} else {self._expr(node.false_value)})'
        if isinstance(node, NullCoalesce):
            val = self._expr(node.value)
            default = self._expr(node.default)
            return f'({val} if {val} is not None else {default})'
        if isinstance(node, StarExpr):
            if node.double:
                return f'**{self._expr(node.value)}'
            return f'*{self._expr(node.value)}'
        return str(node)

    def _map_name(self, name):
        name_map = {
            'T': 'True', 'F': 'False', 'N': 'None',
            'me': 'self', 'init': '__init__',
        }
        return name_map.get(name, name)

    def _map_builtin_func(self, name):
        return BUILTIN_FUNC_MAP.get(name, name)


def transpile(ast, include_preamble=True):
    transpiler = Transpiler()
    return transpiler.transpile(ast, include_preamble)
