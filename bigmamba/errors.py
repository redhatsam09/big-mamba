class MambaError(Exception):

    def __init__(self, message, line=None, col=None, source_line=None):
        self.message = message
        self.line = line
        self.col = col
        self.source_line = source_line
        super().__init__(self.format_error())

    def format_error(self):
        parts = [f"\n--- Big Mamba {self.error_type} ---"]
        parts.append(f"  {self.message}")
        if self.line is not None:
            parts.append(f"  at line {self.line}" + (f", col {self.col}" if self.col else ""))
        if self.source_line is not None:
            parts.append(f"")
            parts.append(f"    {self.source_line.rstrip()}")
            if self.col is not None and self.col > 0:
                parts.append(f"    {' ' * (self.col - 1)}^")
        parts.append(f"{'─' * 35}")
        return "\n".join(parts)

    @property
    def error_type(self):
        return "Error"


class MambaLexerError(MambaError):

    @property
    def error_type(self):
        return "LexerError"


class MambaParserError(MambaError):

    @property
    def error_type(self):
        return "ParserError"


class MambaRuntimeError(MambaError):

    @property
    def error_type(self):
        return "RuntimeError"


class MambaTranspileError(MambaError):

    @property
    def error_type(self):
        return "TranspileError"
