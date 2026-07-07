from .lexer import TokenType, Token
from .ast_nodes import *
from .errors import MambaParserError


class Parser:

    def __init__(self, tokens, source_lines=None):
        self.tokens = tokens
        self.pos = 0
        self.source_lines = source_lines or []

    def error(self, msg):
        token = self.current()
        source_line = self.source_lines[token.line - 1] if token.line <= len(self.source_lines) else None
        raise MambaParserError(msg, token.line, token.col, source_line)

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, '', 0, 0)

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TokenType.EOF, '', 0, 0)

    def advance(self):
        token = self.current()
        self.pos += 1
        return token

    def expect(self, token_type, value=None):
        token = self.current()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name} ('{token.value}')")
        if value is not None and token.value != value:
            self.error(f"Expected '{value}', got '{token.value}'")
        return self.advance()

    def match(self, token_type, value=None):
        token = self.current()
        if token.type == token_type and (value is None or token.value == value):
            return self.advance()
        return None

    def check(self, token_type, value=None):
        token = self.current()
        return token.type == token_type and (value is None or token.value == value)

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE) or self.check(TokenType.COMMENT) or self.check(TokenType.DOCSTRING):
            self.advance()

    def _is_for_loop(self):
        idx = self.pos + 1
        depth = 0
        while idx < len(self.tokens):
            tok = self.tokens[idx]
            if tok.type == TokenType.LPAREN:
                depth += 1
            elif tok.type == TokenType.RPAREN:
                depth -= 1
            elif depth == 0:
                if tok.type == TokenType.KEYWORD and tok.value == 'in':
                    return True
                if tok.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.COLON):
                    return False
            idx += 1
        return False

    def parse(self):
        statements = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return Program(statements)

    def parse_statement(self):
        self.skip_newlines()
        token = self.current()

        if token.type == TokenType.COMMENT:
            self.advance()
            return Comment(token.value, line=token.line)

        if token.type == TokenType.DOCSTRING:
            self.advance()
            return Docstring(token.value, line=token.line)

        if token.type == TokenType.AT:
            if self._is_for_loop():
                return self.parse_expression_statement()
            else:
                return self.parse_decorated()

        if token.type == TokenType.KEYWORD:
            return self.parse_keyword_statement(token)

        if token.type == TokenType.QUESTION:
            return self.parse_if_statement()

        if token.type == TokenType.DOUBLE_DOT:
            self.advance()
            self.consume_end_of_statement()
            return Pass(line=token.line)

        return self.parse_expression_statement()

    def parse_keyword_statement(self, token):
        val = token.value
        if val == 'fn':
            return self.parse_function_def()
        elif val == 'cls':
            return self.parse_class_def()
        elif val == 'ret':
            return self.parse_return()
        elif val == 'yld':
            return self.parse_yield()
        elif val == 'wl':
            return self.parse_while_loop()
        elif val == 'brk':
            self.advance()
            self.consume_end_of_statement()
            return Break(line=token.line)
        elif val == 'cnt':
            self.advance()
            self.consume_end_of_statement()
            return Continue(line=token.line)
        elif val == 'try':
            return self.parse_try_catch()
        elif val == 'throw':
            return self.parse_raise()
        elif val == 'chk':
            return self.parse_assert()
        elif val == 'gl':
            return self.parse_global()
        elif val == 'rm':
            return self.parse_delete()
        elif val == 'use':
            return self.parse_import()
        elif val == 'w/':
            return self.parse_with()
        elif val == 'say':
            return self.parse_say()
        elif val == 'ask':
            return self.parse_expression_statement()
        elif val == 'quit':
            self.advance()
            self.consume_end_of_statement()
            return ExpressionStatement(Call(Name('quit'), [], line=token.line), line=token.line)
        else:
            return self.parse_expression_statement()

    def consume_end_of_statement(self):
        if self.check(TokenType.NEWLINE):
            self.advance()
        elif self.check(TokenType.EOF):
            pass
        elif self.check(TokenType.DEDENT):
            pass
        elif self.check(TokenType.SEMICOLON):
            self.advance()

    def parse_function_def(self, decorators=None):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'fn')
        name_token = self.current()
        if name_token.value == 'init':
            name = '__init__'
            self.advance()
        else:
            name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        params = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        body = self.parse_block()
        return FunctionDef(name, params, body, decorators=decorators, line=line)

    def parse_parameters(self):
        params = []
        while not self.check(TokenType.RPAREN):
            is_args = False
            is_kwargs = False
            if self.match(TokenType.DOUBLE_STAR):
                is_kwargs = True
            elif self.match(TokenType.STAR):
                is_args = True
            if self.check(TokenType.KEYWORD, 'me'):
                name = 'self'
                self.advance()
            else:
                name = self.expect(TokenType.IDENTIFIER).value
            default = None
            if self.match(TokenType.ASSIGN):
                default = self.parse_expression()
            params.append(Parameter(name, default, is_args, is_kwargs))
            if not self.match(TokenType.COMMA):
                break
        return params

    def parse_class_def(self, decorators=None):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'cls')
        name = self.expect(TokenType.IDENTIFIER).value
        bases = []
        if self.match(TokenType.LPAREN):
            while not self.check(TokenType.RPAREN):
                bases.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        body = self.parse_block()
        return ClassDef(name, bases, body, decorators=decorators, line=line)

    def parse_decorated(self):
        decorators = []
        while self.check(TokenType.AT):
            self.advance()
            dec_name = self.parse_expression()
            decorators.append(dec_name)
            self.consume_end_of_statement()
            self.skip_newlines()
        if self.check(TokenType.KEYWORD, 'fn'):
            return self.parse_function_def(decorators=decorators)
        elif self.check(TokenType.KEYWORD, 'cls'):
            return self.parse_class_def(decorators=decorators)
        else:
            self.error("Decorators must be followed by 'fn' or 'cls'")

    def parse_if_statement(self):
        line = self.current().line
        self.expect(TokenType.QUESTION)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        body = self.parse_block()
        elif_clauses = []
        else_body = None
        while True:
            self.skip_newlines()
            if self.check(TokenType.DOUBLE_QUESTION):
                self.advance()
                elif_cond = self.parse_expression()
                self.expect(TokenType.COLON)
                elif_body = self.parse_block()
                elif_clauses.append((elif_cond, elif_body))
            elif self.check(TokenType.EXCLAMATION):
                self.advance()
                self.expect(TokenType.COLON)
                else_body = self.parse_block()
                break
            else:
                break
        return IfStatement(condition, body, elif_clauses, else_body, line=line)

    def parse_while_loop(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'wl')
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        body = self.parse_block()
        return WhileLoop(condition, body, line=line)

    def parse_for_loop(self):
        line = self.current().line
        self.expect(TokenType.AT)
        target = self.parse_target_list()
        self.expect(TokenType.KEYWORD, 'in')
        iterable = self.parse_expression()
        self.expect(TokenType.COLON)
        body = self.parse_block()
        else_body = None
        self.skip_newlines()
        if self.check(TokenType.EXCLAMATION):
            self.advance()
            self.expect(TokenType.COLON)
            else_body = self.parse_block()
        return ForLoop(target, iterable, body, else_body, line=line)

    def parse_target_list(self):
        targets = []
        targets.append(self._parse_target_name())
        while self.match(TokenType.COMMA):
            if self.check(TokenType.KEYWORD, 'in'):
                break
            targets.append(self._parse_target_name())
        if len(targets) == 1:
            return targets[0]
        return TupleLiteral(targets, line=targets[0].line)

    def _parse_target_name(self):
        token = self.current()
        if token.type == TokenType.KEYWORD and token.value == 'me':
            self.advance()
            return Name('self', line=token.line)
        elif token.type in (TokenType.IDENTIFIER, TokenType.BUILTIN):
            self.advance()
            return Name(token.value, line=token.line)
        elif token.type == TokenType.KEYWORD and token.value not in (
                'fn', 'cls', 'ret', 'wl', 'brk', 'cnt', 'catch', 'fin',
                'throw', 'chk', 'gl', 'yld', 'lm', 'rm', 'use', 'try',
                'in', 'is', 'as', 'w/'):
            self.advance()
            return Name(token.value, line=token.line)
        else:
            self.error(f"Expected variable name, got {token.type.name} ('{token.value}')")

    def parse_try_catch(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'try')
        self.expect(TokenType.COLON)
        try_body = self.parse_block()
        except_clauses = []
        else_body = None
        finally_body = None
        while True:
            self.skip_newlines()
            if self.check(TokenType.KEYWORD, 'catch'):
                self.advance()
                exc_type = None
                exc_name = None
                if not self.check(TokenType.COLON):
                    exc_type = self.parse_expression()
                    if self.match(TokenType.KEYWORD, 'as'):
                        exc_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                exc_body = self.parse_block()
                except_clauses.append((exc_type, exc_name, exc_body))
            elif self.check(TokenType.EXCLAMATION):
                self.advance()
                self.expect(TokenType.COLON)
                else_body = self.parse_block()
            elif self.check(TokenType.KEYWORD, 'fin'):
                self.advance()
                self.expect(TokenType.COLON)
                finally_body = self.parse_block()
                break
            else:
                break
        return TryCatch(try_body, except_clauses, else_body, finally_body, line=line)

    def parse_import(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'use')
        module = self.expect(TokenType.IDENTIFIER).value
        while self.match(TokenType.DOT):
            module += '.' + self.expect(TokenType.IDENTIFIER).value
        if self.match(TokenType.ARROW):
            names = []
            if self.match(TokenType.STAR):
                names.append(('*', None))
            else:
                name = self.expect(TokenType.IDENTIFIER).value
                alias = None
                if self.match(TokenType.FAT_ARROW):
                    alias = self.expect(TokenType.IDENTIFIER).value
                names.append((name, alias))
                while self.match(TokenType.COMMA):
                    name = self.expect(TokenType.IDENTIFIER).value
                    alias = None
                    if self.match(TokenType.FAT_ARROW):
                        alias = self.expect(TokenType.IDENTIFIER).value
                    names.append((name, alias))
            self.consume_end_of_statement()
            return ImportFrom(module, names, line=line)
        if self.match(TokenType.FAT_ARROW):
            alias = self.expect(TokenType.IDENTIFIER).value
            self.consume_end_of_statement()
            return Import(module, alias=alias, line=line)
        self.consume_end_of_statement()
        return Import(module, line=line)

    def parse_with(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'w/')
        context = self.parse_expression()
        name = None
        if self.match(TokenType.KEYWORD, 'as'):
            name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        body = self.parse_block()
        return WithStatement(context, name, body, line=line)

    def parse_return(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'ret')
        value = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF) and not self.check(TokenType.DEDENT):
            value = self.parse_expression()
        self.consume_end_of_statement()
        return Return(value, line=line)

    def parse_yield(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'yld')
        value = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF):
            value = self.parse_expression()
        self.consume_end_of_statement()
        return Yield(value, line=line)

    def parse_raise(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'throw')
        exc = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF):
            exc = self.parse_expression()
        self.consume_end_of_statement()
        return Raise(exc, line=line)

    def parse_assert(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'chk')
        test = self.parse_expression()
        msg = None
        if self.match(TokenType.COMMA):
            msg = self.parse_expression()
        self.consume_end_of_statement()
        return Assert(test, msg, line=line)

    def parse_global(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'gl')
        names = [self.expect(TokenType.IDENTIFIER).value]
        while self.match(TokenType.COMMA):
            names.append(self.expect(TokenType.IDENTIFIER).value)
        self.consume_end_of_statement()
        return Global(names, line=line)

    def parse_delete(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'rm')
        target = self.parse_expression()
        self.consume_end_of_statement()
        return Delete(target, line=line)

    def parse_say(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'say')
        args = []
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF) and not self.check(TokenType.DEDENT):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                if self.check(TokenType.NEWLINE) or self.check(TokenType.EOF):
                    break
                args.append(self.parse_expression())
        self.consume_end_of_statement()
        return ExpressionStatement(
            Call(Name('print', line=line), args, line=line),
            line=line
        )

    def parse_expression_statement(self):
        line = self.current().line
        if self.check(TokenType.AT):
            return self.parse_for_loop()
        expr = self.parse_expression()
        if self.check(TokenType.INCREMENT):
            self.advance()
            self.consume_end_of_statement()
            return Increment(expr, line=line)
        if self.check(TokenType.DECREMENT):
            self.advance()
            self.consume_end_of_statement()
            return Decrement(expr, line=line)
        if self.check(TokenType.SWAP):
            self.advance()
            right = self.parse_expression()
            self.consume_end_of_statement()
            return Swap(expr, right, line=line)
        if self.check(TokenType.ASSIGN):
            self.advance()
            targets = [expr]
            while self.check(TokenType.ASSIGN):
                val = self.parse_expression()
                targets.append(val)
                self.advance()
            value = self.parse_expression()
            self.consume_end_of_statement()
            return Assignment(targets, value, line=line)
        aug_ops = {
            TokenType.PLUS_ASSIGN: '+=',
            TokenType.MINUS_ASSIGN: '-=',
            TokenType.STAR_ASSIGN: '*=',
            TokenType.SLASH_ASSIGN: '/=',
            TokenType.DSLASH_ASSIGN: '//=',
            TokenType.PERCENT_ASSIGN: '%=',
            TokenType.POWER_ASSIGN: '**=',
        }
        for tok_type, op_str in aug_ops.items():
            if self.check(tok_type):
                self.advance()
                value = self.parse_expression()
                self.consume_end_of_statement()
                return AugmentedAssignment(expr, op_str, value, line=line)
        self.consume_end_of_statement()
        return ExpressionStatement(expr, line=line)

    def parse_block(self):
        self.skip_newlines()
        if not self.check(TokenType.INDENT):
            stmt = self.parse_statement()
            return [stmt] if stmt else [Pass()]
        self.expect(TokenType.INDENT)
        statements = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        if self.check(TokenType.DEDENT):
            self.advance()
        return statements if statements else [Pass()]

    def parse_expression(self):
        return self.parse_ternary()

    def parse_ternary(self):
        expr = self.parse_null_coalesce()
        if self.check(TokenType.KEYWORD, 'if'):
            self.advance()
            condition = self.parse_or_expr()
            self.expect(TokenType.EXCLAMATION)
            false_value = self.parse_expression()
            return Ternary(condition, expr, false_value, line=expr.line)
        return expr

    def parse_null_coalesce(self):
        expr = self.parse_or_expr()
        while self.check(TokenType.DOUBLE_QUESTION):
            self.advance()
            default = self.parse_or_expr()
            expr = NullCoalesce(expr, default, line=expr.line)
        return expr

    def parse_or_expr(self):
        expr = self.parse_and_expr()
        while self.check(TokenType.OR) or self.check(TokenType.KEYWORD, 'or'):
            self.advance()
            right = self.parse_and_expr()
            expr = BoolOp('or', [expr, right], line=expr.line)
        return expr

    def parse_and_expr(self):
        expr = self.parse_not_expr()
        while self.check(TokenType.AND) or self.check(TokenType.KEYWORD, 'and'):
            self.advance()
            right = self.parse_not_expr()
            expr = BoolOp('and', [expr, right], line=expr.line)
        return expr

    def parse_not_expr(self):
        if self.check(TokenType.NOT) or self.check(TokenType.KEYWORD, 'not'):
            self.advance()
            operand = self.parse_not_expr()
            return NotOp(operand, line=operand.line)
        return self.parse_comparison()

    def parse_comparison(self):
        expr = self.parse_addition()
        ops = []
        comparators = []
        comp_tokens = {
            TokenType.EQ: '==', TokenType.NEQ: '!=',
            TokenType.LT: '<', TokenType.GT: '>',
            TokenType.LTE: '<=', TokenType.GTE: '>=',
        }
        while True:
            if self.current().type in comp_tokens:
                op = comp_tokens[self.current().type]
                self.advance()
                ops.append(op)
                comparators.append(self.parse_addition())
            elif self.check(TokenType.KEYWORD, 'in'):
                self.advance()
                ops.append('in')
                comparators.append(self.parse_addition())
            elif self.check(TokenType.KEYWORD, 'is'):
                self.advance()
                if self.check(TokenType.KEYWORD, 'not') or self.check(TokenType.NOT):
                    self.advance()
                    ops.append('is not')
                else:
                    ops.append('is')
                comparators.append(self.parse_addition())
            elif self.check(TokenType.NOT) or self.check(TokenType.KEYWORD, 'not'):
                next_tok = self.peek()
                if next_tok.type == TokenType.KEYWORD and next_tok.value == 'in':
                    self.advance()
                    self.advance()
                    ops.append('not in')
                    comparators.append(self.parse_addition())
                else:
                    break
            else:
                break
        if ops:
            return Compare(expr, ops, comparators, line=expr.line)
        return expr

    def parse_addition(self):
        expr = self.parse_multiplication()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op = '+' if self.current().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplication()
            expr = BinaryOp(expr, op, right, line=expr.line)
        return expr

    def parse_multiplication(self):
        expr = self.parse_power()
        while self.current().type in (TokenType.STAR, TokenType.SLASH, TokenType.DOUBLE_SLASH, TokenType.PERCENT):
            op_map = {
                TokenType.STAR: '*', TokenType.SLASH: '/',
                TokenType.DOUBLE_SLASH: '//', TokenType.PERCENT: '%',
            }
            op = op_map[self.current().type]
            self.advance()
            right = self.parse_power()
            expr = BinaryOp(expr, op, right, line=expr.line)
        return expr

    def parse_power(self):
        expr = self.parse_unary()
        if self.check(TokenType.DOUBLE_STAR):
            self.advance()
            right = self.parse_power()
            expr = BinaryOp(expr, '**', right, line=expr.line)
        return expr

    def parse_unary(self):
        if self.check(TokenType.MINUS):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp('-', operand, line=operand.line)
        if self.check(TokenType.PLUS):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp('+', operand, line=operand.line)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.LPAREN):
                self.advance()
                args, kwargs = self.parse_call_args()
                self.expect(TokenType.RPAREN)
                expr = Call(expr, args, kwargs, line=expr.line)
            elif self.check(TokenType.LBRACKET):
                self.advance()
                index = self.parse_subscript_index()
                self.expect(TokenType.RBRACKET)
                expr = Subscript(expr, index, line=expr.line)
            elif self.check(TokenType.DOT):
                self.advance()
                if self.current().type in (TokenType.IDENTIFIER, TokenType.KEYWORD, TokenType.BUILTIN):
                    attr_name = self.advance().value
                    method_remap = {
                        'add': 'append', 'addall': 'extend', 'rm': 'remove',
                        'up': 'upper', 'lo': 'lower', 'trim': 'strip',
                        'spl': 'split', 'jn': 'join', 'rep': 'replace',
                        'starts': 'startswith', 'ends': 'endswith',
                        'fmt': 'format', 'ks': 'keys', 'vs': 'values',
                        'its': 'items', 'idx': 'index', 'clr': 'clear',
                        'cp': 'copy', 'upd': 'update', 'ins': 'insert',
                        'srt': 'sort', 'rev': 'reverse',
                        'init': '__init__',
                    }
                    attr_name = method_remap.get(attr_name, attr_name)
                    expr = Attribute(expr, attr_name, line=expr.line)
                else:
                    self.error("Expected attribute name after '.'")
            else:
                break
        return expr

    def parse_call_args(self):
        args = []
        kwargs = []
        while not self.check(TokenType.RPAREN):
            if self.check(TokenType.DOUBLE_STAR):
                self.advance()
                value = self.parse_expression()
                args.append(StarExpr(value, double=True))
            elif self.check(TokenType.STAR):
                self.advance()
                value = self.parse_expression()
                args.append(StarExpr(value, double=False))
            else:
                expr = self.parse_expression()
                if self.check(TokenType.ASSIGN) and isinstance(expr, Name):
                    self.advance()
                    value = self.parse_expression()
                    kwargs.append((expr.name, value))
                else:
                    args.append(expr)
            if not self.match(TokenType.COMMA):
                break
        return args, kwargs

    def parse_subscript_index(self):
        if self.check(TokenType.COLON):
            return self._parse_slice(None)
        expr = self.parse_expression()
        if self.check(TokenType.COLON):
            return self._parse_slice(expr)
        return expr

    def _parse_slice(self, lower):
        self.expect(TokenType.COLON)
        upper = None
        step = None
        if not self.check(TokenType.RBRACKET) and not self.check(TokenType.COLON):
            upper = self.parse_expression()
        if self.match(TokenType.COLON):
            if not self.check(TokenType.RBRACKET):
                step = self.parse_expression()
        return Slice(lower, upper, step)

    def parse_primary(self):
        token = self.current()

        if token.type == TokenType.NUMBER:
            self.advance()
            return Number(token.value, line=token.line)

        if token.type == TokenType.STRING:
            self.advance()
            return String(token.value, line=token.line)

        if token.type == TokenType.FSTRING:
            self.advance()
            return FString(token.value, line=token.line)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Name(token.value, line=token.line)

        if token.type == TokenType.KEYWORD:
            if token.value == 'T':
                self.advance()
                return Name('True', line=token.line)
            elif token.value == 'F':
                self.advance()
                return Name('False', line=token.line)
            elif token.value == 'N':
                self.advance()
                return Name('None', line=token.line)
            elif token.value == 'me':
                self.advance()
                return Name('self', line=token.line)
            elif token.value == 'lm':
                return self.parse_lambda()
            elif token.value == 'ask':
                self.advance()
                if self.check(TokenType.LPAREN):
                    self.advance()
                    args, kwargs = self.parse_call_args()
                    self.expect(TokenType.RPAREN)
                    return Call(Name('input', line=token.line), args, kwargs, line=token.line)
                elif self.check(TokenType.STRING) or self.check(TokenType.FSTRING):
                    arg = self.parse_primary()
                    return Call(Name('input', line=token.line), [arg], line=token.line)
                else:
                    return Call(Name('input', line=token.line), [], line=token.line)
            elif token.value in ('say', 'quit'):
                self.advance()
                return Name(token.value, line=token.line)
            else:
                self.advance()
                return Name(token.value, line=token.line)

        if token.type == TokenType.BUILTIN:
            self.advance()
            return Name(token.value, line=token.line)

        if token.type == TokenType.LPAREN:
            self.advance()
            if self.check(TokenType.RPAREN):
                self.advance()
                return TupleLiteral([], line=token.line)
            expr = self.parse_expression()
            if self.check(TokenType.COMMA):
                elements = [expr]
                while self.match(TokenType.COMMA):
                    if self.check(TokenType.RPAREN):
                        break
                    elements.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return TupleLiteral(elements, line=token.line)
            self.expect(TokenType.RPAREN)
            return expr

        if token.type == TokenType.LBRACKET:
            return self.parse_list_literal()

        if token.type == TokenType.LBRACE:
            return self.parse_dict_or_set_literal()

        if token.type == TokenType.NOT:
            self.advance()
            operand = self.parse_not_expr()
            return NotOp(operand, line=token.line)

        self.error(f"Unexpected token: {token.type.name} ('{token.value}')")

    def parse_lambda(self):
        line = self.current().line
        self.expect(TokenType.KEYWORD, 'lm')
        params = []
        while not self.check(TokenType.COLON):
            if self.check(TokenType.KEYWORD, 'me'):
                params.append('self')
                self.advance()
            else:
                params.append(self.expect(TokenType.IDENTIFIER).value)
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.COLON)
        body = self.parse_expression()
        return Lambda(params, body, line=line)

    def parse_list_literal(self):
        line = self.current().line
        self.expect(TokenType.LBRACKET)
        if self.check(TokenType.RBRACKET):
            self.advance()
            return ListLiteral([], line=line)
        first = self.parse_expression()
        if self.check(TokenType.AT):
            self.advance()
            target = self.parse_target_list()
            self.expect(TokenType.KEYWORD, 'in')
            iterable = self.parse_expression()
            condition = None
            if self.check(TokenType.QUESTION):
                self.advance()
                condition = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            return ListComp(first, target, iterable, condition, line=line)
        elements = [first]
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RBRACKET):
                break
            elements.append(self.parse_expression())
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements, line=line)

    def parse_dict_or_set_literal(self):
        line = self.current().line
        self.expect(TokenType.LBRACE)
        if self.check(TokenType.RBRACE):
            self.advance()
            return DictLiteral([], line=line)
        first = self.parse_expression()
        if self.check(TokenType.COLON):
            self.advance()
            value = self.parse_expression()
            if self.check(TokenType.AT):
                self.advance()
                target = self.parse_target_list()
                self.expect(TokenType.KEYWORD, 'in')
                iterable = self.parse_expression()
                condition = None
                if self.check(TokenType.QUESTION):
                    self.advance()
                    condition = self.parse_expression()
                self.expect(TokenType.RBRACE)
                return DictComp(first, value, target, iterable, condition, line=line)
            pairs = [(first, value)]
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACE):
                    break
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                val = self.parse_expression()
                pairs.append((key, val))
            self.expect(TokenType.RBRACE)
            return DictLiteral(pairs, line=line)
        elements = [first]
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RBRACE):
                break
            elements.append(self.parse_expression())
        self.expect(TokenType.RBRACE)
        return SetLiteral(elements, line=line)


def parse(tokens, source=""):
    source_lines = source.split('\n') if source else []
    parser = Parser(tokens, source_lines)
    return parser.parse()
