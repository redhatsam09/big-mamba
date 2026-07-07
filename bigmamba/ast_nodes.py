class ASTNode:
    def __init__(self, line=None):
        self.line = line

    def __repr__(self):
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if k != 'line')
        return f'{self.__class__.__name__}({attrs})'


class Program(ASTNode):
    def __init__(self, statements):
        super().__init__(line=1)
        self.statements = statements


class ExpressionStatement(ASTNode):
    def __init__(self, expression, line=None):
        super().__init__(line)
        self.expression = expression


class Assignment(ASTNode):
    def __init__(self, targets, value, line=None):
        super().__init__(line)
        self.targets = targets
        self.value = value


class AugmentedAssignment(ASTNode):
    def __init__(self, target, op, value, line=None):
        super().__init__(line)
        self.target = target
        self.op = op
        self.value = value


class Increment(ASTNode):
    def __init__(self, target, line=None):
        super().__init__(line)
        self.target = target


class Decrement(ASTNode):
    def __init__(self, target, line=None):
        super().__init__(line)
        self.target = target


class Swap(ASTNode):
    def __init__(self, left, right, line=None):
        super().__init__(line)
        self.left = left
        self.right = right


class Delete(ASTNode):
    def __init__(self, target, line=None):
        super().__init__(line)
        self.target = target


class Pass(ASTNode):
    pass


class Break(ASTNode):
    pass


class Continue(ASTNode):
    pass


class Return(ASTNode):
    def __init__(self, value=None, line=None):
        super().__init__(line)
        self.value = value


class Yield(ASTNode):
    def __init__(self, value=None, line=None):
        super().__init__(line)
        self.value = value


class Global(ASTNode):
    def __init__(self, names, line=None):
        super().__init__(line)
        self.names = names


class Assert(ASTNode):
    def __init__(self, test, msg=None, line=None):
        super().__init__(line)
        self.test = test
        self.msg = msg


class Raise(ASTNode):
    def __init__(self, exception=None, line=None):
        super().__init__(line)
        self.exception = exception


class IfStatement(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None, line=None):
        super().__init__(line)
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses or []
        self.else_body = else_body


class ForLoop(ASTNode):
    def __init__(self, target, iterable, body, else_body=None, line=None):
        super().__init__(line)
        self.target = target
        self.iterable = iterable
        self.body = body
        self.else_body = else_body


class WhileLoop(ASTNode):
    def __init__(self, condition, body, else_body=None, line=None):
        super().__init__(line)
        self.condition = condition
        self.body = body
        self.else_body = else_body


class TryCatch(ASTNode):
    def __init__(self, try_body, except_clauses=None, else_body=None, finally_body=None, line=None):
        super().__init__(line)
        self.try_body = try_body
        self.except_clauses = except_clauses or []
        self.else_body = else_body
        self.finally_body = finally_body


class WithStatement(ASTNode):
    def __init__(self, context, name, body, line=None):
        super().__init__(line)
        self.context = context
        self.name = name
        self.body = body


class FunctionDef(ASTNode):
    def __init__(self, name, params, body, decorators=None, line=None):
        super().__init__(line)
        self.name = name
        self.params = params
        self.body = body
        self.decorators = decorators or []


class Parameter(ASTNode):
    def __init__(self, name, default=None, is_args=False, is_kwargs=False, line=None):
        super().__init__(line)
        self.name = name
        self.default = default
        self.is_args = is_args
        self.is_kwargs = is_kwargs


class ClassDef(ASTNode):
    def __init__(self, name, bases, body, decorators=None, line=None):
        super().__init__(line)
        self.name = name
        self.bases = bases
        self.body = body
        self.decorators = decorators or []


class Import(ASTNode):
    def __init__(self, module, alias=None, line=None):
        super().__init__(line)
        self.module = module
        self.alias = alias


class ImportFrom(ASTNode):
    def __init__(self, module, names, line=None):
        super().__init__(line)
        self.module = module
        self.names = names


class BinaryOp(ASTNode):
    def __init__(self, left, op, right, line=None):
        super().__init__(line)
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, op, operand, line=None):
        super().__init__(line)
        self.op = op
        self.operand = operand


class Compare(ASTNode):
    def __init__(self, left, ops, comparators, line=None):
        super().__init__(line)
        self.left = left
        self.ops = ops
        self.comparators = comparators


class BoolOp(ASTNode):
    def __init__(self, op, values, line=None):
        super().__init__(line)
        self.op = op
        self.values = values


class NotOp(ASTNode):
    def __init__(self, operand, line=None):
        super().__init__(line)
        self.operand = operand


class Call(ASTNode):
    def __init__(self, func, args, kwargs=None, line=None):
        super().__init__(line)
        self.func = func
        self.args = args
        self.kwargs = kwargs or []


class Attribute(ASTNode):
    def __init__(self, obj, attr, line=None):
        super().__init__(line)
        self.obj = obj
        self.attr = attr


class Subscript(ASTNode):
    def __init__(self, obj, index, line=None):
        super().__init__(line)
        self.obj = obj
        self.index = index


class Slice(ASTNode):
    def __init__(self, lower=None, upper=None, step=None, line=None):
        super().__init__(line)
        self.lower = lower
        self.upper = upper
        self.step = step


class Name(ASTNode):
    def __init__(self, name, line=None):
        super().__init__(line)
        self.name = name


class Number(ASTNode):
    def __init__(self, value, line=None):
        super().__init__(line)
        self.value = value


class String(ASTNode):
    def __init__(self, value, is_fstring=False, line=None):
        super().__init__(line)
        self.value = value
        self.is_fstring = is_fstring


class FString(ASTNode):
    def __init__(self, value, line=None):
        super().__init__(line)
        self.value = value


class ListLiteral(ASTNode):
    def __init__(self, elements, line=None):
        super().__init__(line)
        self.elements = elements


class DictLiteral(ASTNode):
    def __init__(self, pairs, line=None):
        super().__init__(line)
        self.pairs = pairs


class TupleLiteral(ASTNode):
    def __init__(self, elements, line=None):
        super().__init__(line)
        self.elements = elements


class SetLiteral(ASTNode):
    def __init__(self, elements, line=None):
        super().__init__(line)
        self.elements = elements


class ListComp(ASTNode):
    def __init__(self, element, target, iterable, condition=None, line=None):
        super().__init__(line)
        self.element = element
        self.target = target
        self.iterable = iterable
        self.condition = condition


class DictComp(ASTNode):
    def __init__(self, key, value, target, iterable, condition=None, line=None):
        super().__init__(line)
        self.key = key
        self.value = value
        self.target = target
        self.iterable = iterable
        self.condition = condition


class Lambda(ASTNode):
    def __init__(self, params, body, line=None):
        super().__init__(line)
        self.params = params
        self.body = body


class Ternary(ASTNode):
    def __init__(self, condition, true_value, false_value, line=None):
        super().__init__(line)
        self.condition = condition
        self.true_value = true_value
        self.false_value = false_value


class NullCoalesce(ASTNode):
    def __init__(self, value, default, line=None):
        super().__init__(line)
        self.value = value
        self.default = default


class StarExpr(ASTNode):
    def __init__(self, value, double=False, line=None):
        super().__init__(line)
        self.value = value
        self.double = double


class Comment(ASTNode):
    def __init__(self, text, line=None):
        super().__init__(line)
        self.text = text


class Docstring(ASTNode):
    def __init__(self, text, line=None):
        super().__init__(line)
        self.text = text
