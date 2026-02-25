
# ============================================================
#  Eusha Language - Lexer
#  Converts raw source code into a stream of tokens.
# ============================================================

import re

# ------ Token Types ------
TT_INT        = 'INT'
TT_FLOAT      = 'FLOAT'
TT_STRING     = 'STRING'
TT_FSTRING    = 'FSTRING'   # interpolated string parts
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD    = 'KEYWORD'
TT_PLUS       = 'PLUS'
TT_MINUS      = 'MINUS'
TT_MUL        = 'MUL'
TT_DIV        = 'DIV'
TT_MOD        = 'MOD'
TT_POW        = 'POW'
TT_EQ         = 'EQ'        # =
TT_PLUSEQ     = 'PLUSEQ'    # +=
TT_MINUSEQ    = 'MINUSEQ'   # -=
TT_MULEQ      = 'MULEQ'     # *=
TT_DIVEQ      = 'DIVEQ'     # /=
TT_EQEQ       = 'EQEQ'     # ==
TT_NEQ        = 'NEQ'       # !=
TT_LT         = 'LT'        # <
TT_GT         = 'GT'        # >
TT_LTE        = 'LTE'       # <=
TT_GTE        = 'GTE'       # >=
TT_LPAREN     = 'LPAREN'    # (
TT_RPAREN     = 'RPAREN'    # )
TT_LBRACE     = 'LBRACE'    # {
TT_RBRACE     = 'RBRACE'    # }
TT_LBRACKET   = 'LBRACKET'  # [
TT_RBRACKET   = 'RBRACKET'  # ]
TT_COMMA      = 'COMMA'     # ,
TT_COLON      = 'COLON'     # :
TT_DOT        = 'DOT'       # .
TT_DOTDOT     = 'DOTDOT'    # ..
TT_ARROW      = 'ARROW'     # ->
TT_FATARROW   = 'FATARROW'  # =>
TT_CMDPREFIX  = 'CMDPREFIX'  # &&
TT_NEWLINE    = 'NEWLINE'
TT_EOF        = 'EOF'

KEYWORDS = {
    'fn', 'return', 'if', 'else', 'while', 'for', 'in',
    'step', 'reverse', 'say', 'take', 'and', 'or', 'not',
    'true', 'false', 'none', 'use', 'break', 'continue'
}


class Token:
    def __init__(self, type_, value=None, line=0, column=0):
        self.type   = type_
        self.value  = value
        self.line   = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'


class LexerError(Exception):
    def __init__(self, msg, line, column=0, hint=""):
        self.line = line
        self.column = column
        self.msg = msg
        self.hint = hint
        super().__init__(f'[Line {line}] Lexer Error: {msg}')


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.column = 1
        self.tokens : list[Token] = []

    def current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def skip_whitespace(self):
        while self.current() in (' ', '\t', '\r'):
            self.advance()

    def skip_comment(self):
        # Comments start with $$
        while self.current() is not None and self.current() != '\n':
            self.advance()

    def read_string(self, quote_char):
        start_col = self.column
        start_line = self.line
        self.advance()  # skip opening quote
        result = []
        has_interpolation = False
        interp_parts = []  # list of (type, value): 'str' or 'expr'
        current_str = []

        while self.current() is not None and self.current() != quote_char:
            if self.current() == '\\' :
                self.advance()
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', "'": "'", '"': '"', '{': '{'}
                current_str.append(escape_map.get(esc, esc))
            elif self.current() == '{' and quote_char == '"':
                # String interpolation: {expression}
                has_interpolation = True
                if current_str:
                    interp_parts.append(('str', ''.join(current_str)))
                    current_str = []
                self.advance()  # skip '{'
                expr_chars = []
                depth = 1
                while self.current() is not None and depth > 0:
                    if self.current() == '{':
                        depth += 1
                    elif self.current() == '}':
                        depth -= 1
                        if depth == 0:
                            break
                    expr_chars.append(self.advance())
                if self.current() != '}':
                    raise LexerError('Unterminated string interpolation', self.line, self.column, 'Did you forget a closing }?')
                self.advance()  # skip '}'
                interp_parts.append(('expr', ''.join(expr_chars)))
            else:
                current_str.append(self.advance())

        if self.current() != quote_char:
            raise LexerError('Unterminated string literal', start_line, start_col, 'Did you forget to close the quote?')
        self.advance()  # skip closing quote

        if has_interpolation:
            if current_str:
                interp_parts.append(('str', ''.join(current_str)))
            return ('fstring', interp_parts)
        return ('string', ''.join(current_str))

    def read_number(self):
        start = self.pos
        is_float = False
        while self.current() is not None and self.current().isdigit():
            self.advance()
        if self.current() == '.' and self.peek() != '.':
            is_float = True
            self.advance()
            while self.current() is not None and self.current().isdigit():
                self.advance()
        text = self.source[start:self.pos]
        if is_float:
            return TT_FLOAT, float(text)
        return TT_INT, int(text)

    def read_identifier(self):
        start = self.pos
        while self.current() is not None and (self.current().isalnum() or self.current() == '_'):
            self.advance()
        word = self.source[start:self.pos]
        if word in KEYWORDS:
            return TT_KEYWORD, word
        return TT_IDENTIFIER, word

    def tokenize(self) -> list[Token]:
        while self.current() is not None:
            self.skip_whitespace()
            ch = self.current()
            line = self.line
            column = self.column

            if ch is None:
                break

            # Comment
            if ch == '$' and self.peek() == '$':
                self.advance(); self.advance()
                self.skip_comment()
                continue

            # Newline
            if ch == '\n':
                self.advance()
                self.tokens.append(Token(TT_NEWLINE, None, line, column))
                continue

            # String literals
            if ch in ('"', "'"):
                result = self.read_string(ch)
                if result[0] == 'fstring':
                    self.tokens.append(Token(TT_FSTRING, result[1], line, column))
                else:
                    self.tokens.append(Token(TT_STRING, result[1], line, column))
                continue

            # Numbers
            if ch.isdigit():
                tt, val = self.read_number()
                self.tokens.append(Token(tt, val, line, column))
                continue

            # Identifiers / keywords
            if ch.isalpha() or ch == '_':
                tt, val = self.read_identifier()
                self.tokens.append(Token(tt, val, line, column))
                continue

            # Two-char operators first
            two = ch + (self.peek() or '')
            if two == '**':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_POW, '**', line, column)); continue
            if two == '..':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_DOTDOT, '..', line, column)); continue
            if two == '=>':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_FATARROW, '=>', line, column)); continue
            if two == '->':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_ARROW, '->', line, column)); continue
            if two == '+=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_PLUSEQ, '+=', line, column)); continue
            if two == '-=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_MINUSEQ, '-=', line, column)); continue
            if two == '*=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_MULEQ, '*=', line, column)); continue
            if two == '/=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_DIVEQ, '/=', line, column)); continue
            if two == '==':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_EQEQ, '==', line, column)); continue
            if two == '!=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_NEQ, '!=', line, column)); continue
            if two == '<=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_LTE, '<=', line, column)); continue
            if two == '>=':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_GTE, '>=', line, column)); continue

            # Single-char operators
            # && command prefix
            if two == '&&':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_CMDPREFIX, '&&', line, column)); continue

            simple = {
                '+': TT_PLUS, '-': TT_MINUS, '*': TT_MUL, '/': TT_DIV,
                '%': TT_MOD,  '=': TT_EQ,    '<': TT_LT,  '>': TT_GT,
                '(': TT_LPAREN, ')': TT_RPAREN,
                '{': TT_LBRACE, '}': TT_RBRACE,
                '[': TT_LBRACKET, ']': TT_RBRACKET,
                ',': TT_COMMA,  '.': TT_DOT, ':': TT_COLON,
            }
            if ch in simple:
                self.advance()
                self.tokens.append(Token(simple[ch], ch, line, column))
                continue

            raise LexerError(f"Unknown character '{ch}'", line, column, "Remove the character or check for a typo.")

        self.tokens.append(Token(TT_EOF, None, self.line, self.column))
        return self.tokens
