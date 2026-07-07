import re
from enum import Enum, auto
from .errors import MambaLexerError


class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    FSTRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    BUILTIN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    DOUBLE_STAR = auto()
    SLASH = auto()
    DOUBLE_SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()
    DSLASH_ASSIGN = auto()
    PERCENT_ASSIGN = auto()
    POWER_ASSIGN = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    SWAP = auto()
    NULL_COALESCE = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    AT = auto()
    QUESTION = auto()
    DOUBLE_QUESTION = auto()
    EXCLAMATION = auto()
    DOUBLE_DOT = auto()
    WITH_SLASH = auto()
    DOLLAR_STRING = auto()
    HASH = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    COMMENT = auto()
    DOCSTRING = auto()
    EOF = auto()


class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f'Token({self.type.name}, {self.value!r}, L{self.line}:{self.col})'


KEYWORDS = {
    'fn', 'ret', 'cls', 'wl', 'brk', 'cnt', 'catch', 'fin',
    'throw', 'chk', 'gl', 'yld', 'lm', 'rm', 'use',
    'T', 'F', 'N',
    'try', 'in', 'is', 'as', 'say', 'ask',
    'me', 'init', 'quit',
    'and', 'or', 'not',
}

BUILTINS = {
    'l', 'rng', 'i', 's', 'fl', 'ls', 'dt', 'tp', 'st', 'bl',
    'typ', 'isa', 'enum', 'zp', 'mp', 'flt', 'srt', 'rev',
    'ab', 'mx', 'mn', 'sm', 'rnd', 'opn', 'nxt', 'hsh',
    'chr_', 'ord_', 'hex_', 'oct_', 'bin_', 'any_', 'all_',
    'say', 'ask', 'print', 'input', 'len', 'range', 'int', 'str',
    'float', 'list', 'dict', 'tuple', 'set', 'bool', 'type',
}


class Lexer:

    def __init__(self, source, filename="<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]
        self.paren_depth = 0
        self.source_lines = source.split('\n')

    def error(self, msg):
        source_line = self.source_lines[self.line - 1] if self.line <= len(self.source_lines) else None
        raise MambaLexerError(msg, self.line, self.col, source_line)

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected):
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def add_token(self, type, value=None):
        self.tokens.append(Token(type, value, self.line, self.col))

    def tokenize(self):
        self.tokens = []
        while self.pos < len(self.source):
            self._process_line()
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token(TokenType.DEDENT, '<DEDENT>')
        self.add_token(TokenType.EOF, '')
        return self.tokens

    def _process_line(self):
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.advance()
            return
        if self.paren_depth == 0:
            self._handle_indentation()
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self._next_token()
        if self.paren_depth == 0 and self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self.add_token(TokenType.NEWLINE, '\\n')
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.advance()

    def _handle_indentation(self):
        indent = 0
        while self.pos < len(self.source) and self.source[self.pos] in ' \t':
            if self.source[self.pos] == '\t':
                indent += 4
            else:
                indent += 1
            self.advance()
        if self.pos >= len(self.source) or self.source[self.pos] == '\n':
            return
        if self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] == '//' and \
           (self.pos + 2 >= len(self.source) or self.source[self.pos+2] != '/'):
            return
        current_indent = self.indent_stack[-1]
        if indent > current_indent:
            self.indent_stack.append(indent)
            self.add_token(TokenType.INDENT, '<INDENT>')
        elif indent < current_indent:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.add_token(TokenType.DEDENT, '<DEDENT>')
            if self.indent_stack[-1] != indent:
                self.error(f"Indentation error: unexpected indent level {indent}, expected {self.indent_stack[-1]}")

    def _next_token(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t':
            self.advance()
        if self.pos >= len(self.source) or self.source[self.pos] == '\n':
            return

        ch = self.source[self.pos]
        line = self.line
        col = self.col

        if ch == '/' and self.peek(1) == '/':
            if self.peek(2) == '/':
                self.advance()
                self.advance()
                self.advance()
                text = ''
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    text += self.advance()
                self.tokens.append(Token(TokenType.DOCSTRING, text.strip(), line, col))
                return
            else:
                self.advance()
                self.advance()
                text = ''
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    text += self.advance()
                self.tokens.append(Token(TokenType.COMMENT, text.strip(), line, col))
                return

        if ch == '$' and self.peek(1) == '"':
            self.advance()
            self.advance()
            value = self._read_string_content('"')
            self.tokens.append(Token(TokenType.FSTRING, value, line, col))
            return

        if ch in ('"', "'"):
            token = self._read_string(ch)
            self.tokens.append(Token(token[0], token[1], line, col))
            return

        if ch.isdigit() or (ch == '.' and self.peek(1).isdigit()):
            value = self._read_number()
            self.tokens.append(Token(TokenType.NUMBER, value, line, col))
            return

        if ch.isalpha() or ch == '_':
            value = self._read_identifier()
            if value == 'w' and self.pos < len(self.source) and self.source[self.pos] == '/':
                self.advance()
                self.tokens.append(Token(TokenType.KEYWORD, 'w/', line, col))
                return
            if value in KEYWORDS:
                self.tokens.append(Token(TokenType.KEYWORD, value, line, col))
            elif value in BUILTINS:
                self.tokens.append(Token(TokenType.BUILTIN, value, line, col))
            else:
                self.tokens.append(Token(TokenType.IDENTIFIER, value, line, col))
            return

        self.advance()

        if ch == '?' and self.peek() == '?':
            self.advance()
            self.tokens.append(Token(TokenType.DOUBLE_QUESTION, '??', line, col))
            return
        if ch == '?':
            self.tokens.append(Token(TokenType.QUESTION, '?', line, col))
            return
        if ch == '!':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.NEQ, '!=', line, col))
            else:
                self.tokens.append(Token(TokenType.EXCLAMATION, '!', line, col))
            return
        if ch == '&' and self.peek() == '&':
            self.advance()
            self.tokens.append(Token(TokenType.AND, '&&', line, col))
            return
        if ch == '|' and self.peek() == '|':
            self.advance()
            self.tokens.append(Token(TokenType.OR, '||', line, col))
            return
        if ch == '~':
            self.tokens.append(Token(TokenType.NOT, '~', line, col))
            return
        if ch == '.':
            if self.peek() == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOUBLE_DOT, '..', line, col))
            else:
                self.tokens.append(Token(TokenType.DOT, '.', line, col))
            return
        if ch == '+':
            if self.peek() == '+':
                self.advance()
                self.tokens.append(Token(TokenType.INCREMENT, '++', line, col))
            elif self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', line, col))
            else:
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
            return
        if ch == '-':
            if self.peek() == '-':
                self.advance()
                self.tokens.append(Token(TokenType.DECREMENT, '--', line, col))
            elif self.peek() == '>':
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '->', line, col))
            elif self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', line, col))
            else:
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
            return
        if ch == '*':
            if self.peek() == '*':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.POWER_ASSIGN, '**=', line, col))
                else:
                    self.tokens.append(Token(TokenType.DOUBLE_STAR, '**', line, col))
            elif self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.STAR_ASSIGN, '*=', line, col))
            else:
                self.tokens.append(Token(TokenType.STAR, '*', line, col))
            return
        if ch == '/':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.SLASH_ASSIGN, '/=', line, col))
            elif self.peek() == '/':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.DSLASH_ASSIGN, '//=', line, col))
                else:
                    self.tokens.append(Token(TokenType.DOUBLE_SLASH, '//', line, col))
            else:
                self.tokens.append(Token(TokenType.SLASH, '/', line, col))
            return
        if ch == '%':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.PERCENT_ASSIGN, '%=', line, col))
            else:
                self.tokens.append(Token(TokenType.PERCENT, '%', line, col))
            return
        if ch == '=':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.EQ, '==', line, col))
            elif self.peek() == '>':
                self.advance()
                self.tokens.append(Token(TokenType.FAT_ARROW, '=>', line, col))
            else:
                self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
            return
        if ch == '<':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.LTE, '<=', line, col))
            elif self.peek() == '>':
                self.advance()
                self.tokens.append(Token(TokenType.SWAP, '<>', line, col))
            else:
                self.tokens.append(Token(TokenType.LT, '<', line, col))
            return
        if ch == '>':
            if self.peek() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.GTE, '>=', line, col))
            else:
                self.tokens.append(Token(TokenType.GT, '>', line, col))
            return

        simple = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            '@': TokenType.AT,
            '#': TokenType.HASH,
        }
        if ch in simple:
            if ch in ('(', '[', '{'):
                self.paren_depth += 1
            elif ch in (')', ']', '}'):
                self.paren_depth = max(0, self.paren_depth - 1)
            self.tokens.append(Token(simple[ch], ch, line, col))
            return

        self.error(f"Unexpected character: '{ch}'")

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.advance()
        return self.source[start:self.pos]

    def _read_number(self):
        start = self.pos
        has_dot = False
        if self.source[self.pos] == '0' and self.pos + 1 < len(self.source):
            next_ch = self.source[self.pos + 1].lower()
            if next_ch in ('x', 'o', 'b'):
                self.advance()
                self.advance()
                while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    self.advance()
                return self.source[start:self.pos]
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isdigit() or ch == '_':
                self.advance()
            elif ch == '.' and not has_dot and self.peek(1).isdigit():
                has_dot = True
                self.advance()
            elif ch in ('e', 'E'):
                self.advance()
                if self.pos < len(self.source) and self.source[self.pos] in ('+', '-'):
                    self.advance()
            else:
                break
        return self.source[start:self.pos]

    def _read_string(self, quote):
        self.advance()
        if self.peek() == quote and self.peek(1) == quote:
            self.advance()
            self.advance()
            return (TokenType.STRING, self._read_triple_string(quote))
        value = self._read_string_content(quote)
        return (TokenType.STRING, value)

    def _read_string_content(self, quote):
        value = ''
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == '\\':
                self.advance()
                if self.pos < len(self.source):
                    escaped = self.advance()
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', "'": "'", '"': '"'}
                    value += escape_map.get(escaped, '\\' + escaped)
                continue
            if ch == quote:
                self.advance()
                return value
            if ch == '\n':
                self.error("Unterminated string literal")
            value += self.advance()
        self.error("Unterminated string literal")

    def _read_triple_string(self, quote):
        value = ''
        while self.pos < len(self.source):
            if self.source[self.pos] == quote and self.peek(1) == quote and self.peek(2) == quote:
                self.advance()
                self.advance()
                self.advance()
                return value
            value += self.advance()
        self.error("Unterminated triple-quoted string")


def tokenize(source, filename="<stdin>"):
    lexer = Lexer(source, filename)
    return lexer.tokenize()
