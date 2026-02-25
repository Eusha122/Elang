
# ============================================================
#  Eusha Language - Parser
#  Converts a stream of tokens into an AST.
# ============================================================

from lexer import *
from nodes import *


class ParseError(Exception):
    def __init__(self, msg, line=0, column=0, hint=""):
        self.line = line
        self.column = column
        self.msg = msg
        self.hint = hint
        super().__init__(f'[Line {line}] Parse Error: {msg}')


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0

    # ---- helpers ----
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, type_, value=None) -> Token:
        tok = self.current()
        if tok.type != type_:
            hint = ""
            if type_ == TT_RBRACE:
                hint = "Did you forget to close a block with '}'?"
            elif type_ == TT_RPAREN:
                hint = "Did you forget a closing ')'?"
            elif type_ == TT_RBRACKET:
                hint = "Did you forget a closing ']'?"
            raise ParseError(
                f"Expected {type_!r}, got {tok.type!r} ({tok.value!r})",
                tok.line, tok.column, hint
            )
        if value is not None and tok.value != value:
            raise ParseError(
                f"Expected '{value}', got '{tok.value}'",
                tok.line, tok.column
            )
        return self.advance()

    def skip_newlines(self):
        while self.current().type == TT_NEWLINE:
            self.advance()

    def match(self, type_, value=None) -> bool:
        tok = self.current()
        if tok.type != type_:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    # ---- parse entry ----
    def parse(self) -> BlockNode:
        stmts = []
        self.skip_newlines()
        while not self.match(TT_EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self.skip_newlines()
        return BlockNode(stmts)

    # ---- statements ----
    def parse_statement(self) -> Node:
        tok = self.current()

        # Function definition
        if tok.type == TT_KEYWORD and tok.value == 'fn':
            return self.parse_function_def()

        # Return
        if tok.type == TT_KEYWORD and tok.value == 'return':
            return self.parse_return()

        # If
        if tok.type == TT_KEYWORD and tok.value == 'if':
            return self.parse_if()

        # While
        if tok.type == TT_KEYWORD and tok.value == 'while':
            return self.parse_while()

        # For
        if tok.type == TT_KEYWORD and tok.value == 'for':
            return self.parse_for()

        # say(...)
        if tok.type == TT_KEYWORD and tok.value == 'say':
            return self.parse_say()

        # use module
        if tok.type == TT_KEYWORD and tok.value == 'use':
            return self.parse_use()

        # break
        if tok.type == TT_KEYWORD and tok.value == 'break':
            self.advance()
            return BreakNode()

        # continue
        if tok.type == TT_KEYWORD and tok.value == 'continue':
            self.advance()
            return ContinueNode()

        # &&builtin command
        if tok.type == TT_CMDPREFIX:
            return self.parse_builtin_command()

        # Assignment:  name = expr   OR   name[index] = expr  OR  name += expr
        if tok.type == TT_IDENTIFIER:
            # Simple assignment:  name = expr
            if self.peek().type == TT_EQ:
                return self.parse_assignment()
            # Compound assignment: name += expr, name -= expr, etc.
            if self.peek().type in (TT_PLUSEQ, TT_MINUSEQ, TT_MULEQ, TT_DIVEQ):
                return self.parse_compound_assignment()
            # Indexed assignment: name[expr] = expr
            if self.peek().type == TT_LBRACKET:
                return self.parse_possible_index_assignment()

        # Default: expression statement
        return self.parse_expression()

    def parse_assignment(self) -> AssignNode:
        name = self.advance().value   # identifier
        self.advance()               # consume '='
        value = self.parse_expression()
        return AssignNode(name, value)

    def parse_compound_assignment(self) -> CompoundAssignNode:
        name = self.advance().value   # identifier
        op_tok = self.advance()       # consume +=, -=, *=, /=
        op_map = {'+=': '+', '-=': '-', '*=': '*', '/=': '/'}
        op = op_map[op_tok.value]
        value = self.parse_expression()
        return CompoundAssignNode(name, op, value)

    def parse_possible_index_assignment(self):
        """Parse name[index] = value  OR  just name[index] as expression."""
        saved_pos = self.pos
        name_tok = self.advance()  # identifier
        self.advance()  # '['
        index = self.parse_expression()
        self.expect(TT_RBRACKET)
        if self.match(TT_EQ):
            self.advance()  # '='
            value = self.parse_expression()
            return IndexSetNode(IdentifierNode(name_tok.value), index, value)
        # Not an assignment, rewind and parse as expression
        self.pos = saved_pos
        return self.parse_expression()

    def parse_return(self) -> ReturnNode:
        self.advance()  # 'return'
        if self.current().type in (TT_NEWLINE, TT_RBRACE, TT_EOF):
            return ReturnNode(NoneNode())
        value = self.parse_expression()
        return ReturnNode(value)

    def parse_function_def(self) -> FunctionDefNode:
        self.advance()  # 'fn'
        name = self.expect(TT_IDENTIFIER).value
        self.expect(TT_LPAREN)
        params = []
        while not self.match(TT_RPAREN):
            params.append(self.expect(TT_IDENTIFIER).value)
            if self.match(TT_COMMA):
                self.advance()
        self.expect(TT_RPAREN)

        return_type = None
        if self.match(TT_ARROW):
            self.advance()
            return_type = self.advance().value  # e.g. 'int', 'float', etc.

        body = self.parse_block()
        return FunctionDefNode(name, params, body, return_type)

    def parse_if(self) -> IfNode:
        self.advance()  # 'if'
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        self.skip_newlines()
        if self.match(TT_KEYWORD, 'else'):
            self.advance()
            if self.match(TT_KEYWORD, 'if'):
                else_block = self.parse_if()
            else:
                else_block = self.parse_block()
        return IfNode(condition, then_block, else_block)

    def parse_while(self) -> WhileNode:
        self.advance()  # 'while'
        self.expect(TT_LPAREN)
        condition = self.parse_expression()
        self.expect(TT_RPAREN)
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_for(self):
        """
        for (i in 1..10) { }
        for (i in 1..10 step 2) { }
        for (i in 10..1 reverse) { }
        for (x in collection) { }
        """
        self.advance()  # 'for'
        self.expect(TT_LPAREN)
        var = self.expect(TT_IDENTIFIER).value
        self.expect(TT_KEYWORD, 'in')

        start_expr = self.parse_expression()

        if self.match(TT_DOTDOT):
            self.advance()  # '..'
            end_expr = self.parse_expression()
            step_expr = None
            reverse   = False
            if self.match(TT_KEYWORD, 'step'):
                self.advance()
                step_expr = self.parse_expression()
            if self.match(TT_KEYWORD, 'reverse'):
                self.advance()
                reverse = True
            self.expect(TT_RPAREN)
            body = self.parse_block()
            return ForRangeNode(var, start_expr, end_expr, step_expr, reverse, body)
        else:
            # for-each: for (x in collection)
            self.expect(TT_RPAREN)
            body = self.parse_block()
            return ForEachNode(var, start_expr, body)

    def parse_say(self) -> SayNode:
        self.advance()  # 'say'
        self.expect(TT_LPAREN)
        # Empty say()
        if self.match(TT_RPAREN):
            self.advance()
            expr = StringNode('')
        else:
            # Parse first expression
            first = self.parse_expression()
            # Multi-arg say: say(a, b, c) -> concatenate with spaces
            if self.match(TT_COMMA):
                parts = [first]
                while self.match(TT_COMMA):
                    self.advance()
                    parts.append(self.parse_expression())
                # Build a chain of BinOpNode(+) with spaces between
                expr = parts[0]
                for part in parts[1:]:
                    expr = BinOpNode(
                        BinOpNode(expr, '+', StringNode(' ')),
                        '+', part
                    )
            else:
                expr = first
            self.expect(TT_RPAREN)
        # Collect modifiers: .newl .space .tab
        modifiers = []
        while self.match(TT_DOT):
            next_tok = self.peek()
            if next_tok.type not in (TT_IDENTIFIER, TT_KEYWORD):
                break
            self.advance()  # '.'
            mod = self.advance().value
            if mod not in ('newl', 'space', 'tab'):
                raise ParseError(
                    f"Unknown say modifier '{mod}'",
                    self.current().line, self.current().column,
                    "Valid modifiers are: .newl, .space, .tab"
                )
            modifiers.append(mod)
        return SayNode(expr, modifiers)

    def parse_use(self) -> UseNode:
        self.advance()  # 'use'
        name = self.expect(TT_IDENTIFIER).value
        return UseNode(name)

    def parse_block(self) -> BlockNode:
        self.skip_newlines()
        if self.match(TT_EOF):
            raise ParseError(
                "Expected '{' but found end of file",
                self.current().line, self.current().column,
                "Did you forget to open a block with '{'?"
            )
        self.expect(TT_LBRACE)
        self.skip_newlines()
        stmts = []
        while not self.match(TT_RBRACE) and not self.match(TT_EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self.skip_newlines()
        if self.match(TT_EOF):
            raise ParseError(
                "Expected '}' but found end of file",
                self.current().line, self.current().column,
                "Did you forget to close a block with '}'?"
            )
        self.expect(TT_RBRACE)
        return BlockNode(stmts)

    # ---- expressions (Pratt-style precedence) ----
    def parse_expression(self) -> Node:
        return self.parse_or()

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.match(TT_KEYWORD, 'or'):
            op = self.advance().value
            right = self.parse_and()
            left = BinOpNode(left, op, right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_not()
        while self.match(TT_KEYWORD, 'and'):
            op = self.advance().value
            right = self.parse_not()
            left = BinOpNode(left, op, right)
        return left

    def parse_not(self) -> Node:
        if self.match(TT_KEYWORD, 'not'):
            op = self.advance().value
            operand = self.parse_not()
            return UnaryOpNode(op, operand)
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        left = self.parse_add_sub()
        cmp_types = {TT_EQEQ, TT_NEQ, TT_LT, TT_GT, TT_LTE, TT_GTE}
        while self.current().type in cmp_types:
            op = self.advance().value
            right = self.parse_add_sub()
            left = BinOpNode(left, op, right)
        return left

    def parse_add_sub(self) -> Node:
        left = self.parse_mul_div()
        while self.current().type in (TT_PLUS, TT_MINUS):
            op = self.advance().value
            right = self.parse_mul_div()
            left = BinOpNode(left, op, right)
        return left

    def parse_mul_div(self) -> Node:
        left = self.parse_power()
        while self.current().type in (TT_MUL, TT_DIV, TT_MOD):
            op = self.advance().value
            right = self.parse_power()
            left = BinOpNode(left, op, right)
        return left

    def parse_power(self) -> Node:
        left = self.parse_unary()
        if self.current().type == TT_POW:
            op = self.advance().value
            right = self.parse_power()  # right-associative
            return BinOpNode(left, op, right)
        return left

    def parse_unary(self) -> Node:
        if self.current().type == TT_MINUS:
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(op, operand)
        return self.parse_postfix()

    def parse_postfix(self) -> Node:
        """Handle method calls (.method()), indexing ([expr]), and dot access."""
        node = self.parse_primary()
        while True:
            # Method call: expr.method() or expr.method(args)
            if self.match(TT_DOT):
                # Accept both identifiers and keywords as method names
                # (e.g. .reverse, .step, .in are valid method names)
                next_tok = self.peek()
                if next_tok.type in (TT_IDENTIFIER, TT_KEYWORD):
                    self.advance()  # '.'
                    method = self.advance().value
                    args = []
                    if self.match(TT_LPAREN):
                        self.advance()  # '('
                        while not self.match(TT_RPAREN):
                            args.append(self.parse_expression())
                            if self.match(TT_COMMA):
                                self.advance()
                        self.expect(TT_RPAREN)
                    node = MethodCallNode(node, method, args)
                else:
                    break
            # Indexing: expr[index]
            elif self.match(TT_LBRACKET):
                self.advance()  # '['
                index = self.parse_expression()
                self.expect(TT_RBRACKET)
                node = IndexGetNode(node, index)
            else:
                break
        return node

    def parse_primary(self) -> Node:
        tok = self.current()

        # Literals
        if tok.type == TT_INT:
            self.advance()
            return NumberNode(tok.value)
        if tok.type == TT_FLOAT:
            self.advance()
            return NumberNode(tok.value)
        if tok.type == TT_STRING:
            self.advance()
            return StringNode(tok.value)
        if tok.type == TT_FSTRING:
            self.advance()
            return self.parse_fstring(tok.value)
        if tok.type == TT_KEYWORD and tok.value == 'true':
            self.advance()
            return BoolNode(True)
        if tok.type == TT_KEYWORD and tok.value == 'false':
            self.advance()
            return BoolNode(False)
        if tok.type == TT_KEYWORD and tok.value == 'none':
            self.advance()
            return NoneNode()

        # take()
        if tok.type == TT_KEYWORD and tok.value == 'take':
            return self.parse_take()

        # say() as expression
        if tok.type == TT_KEYWORD and tok.value == 'say':
            return self.parse_say()

        # Identifier — possibly a function call or lambda param
        if tok.type == TT_IDENTIFIER:
            # Check for single-param lambda:  name => expr
            if self.peek().type == TT_FATARROW:
                param = self.advance().value  # identifier
                self.advance()  # '=>'
                body = self.parse_expression()
                return LambdaNode([param], body)
            name = self.advance().value
            if self.match(TT_LPAREN):
                return self.parse_call(name)
            return IdentifierNode(name)

        # Array literal: [expr, expr, ...]
        if tok.type == TT_LBRACKET:
            return self.parse_list()

        # Grouped expression or multi-param lambda
        if tok.type == TT_LPAREN:
            return self.parse_paren_or_lambda()

        # Object literal: {key: value, ...}
        if tok.type == TT_LBRACE:
            return self.parse_object_literal()

        raise ParseError(
            f"Unexpected token {tok.type!r} ({tok.value!r})",
            tok.line, tok.column,
            "Check your syntax near this location."
        )

    def parse_paren_or_lambda(self):
        """Parse either (expr) grouped expression or (params) => expr lambda."""
        # Try to detect lambda pattern: (id, id, ...) =>
        saved_pos = self.pos
        self.advance()  # '('

        # Check if this looks like a lambda parameter list
        might_be_lambda = True
        params = []
        if self.match(TT_IDENTIFIER):
            params.append(self.advance().value)
            while self.match(TT_COMMA):
                self.advance()
                if self.match(TT_IDENTIFIER):
                    params.append(self.advance().value)
                else:
                    might_be_lambda = False
                    break
            if might_be_lambda and self.match(TT_RPAREN):
                self.advance()  # ')'
                if self.match(TT_FATARROW):
                    self.advance()  # '=>'
                    body = self.parse_expression()
                    return LambdaNode(params, body)
        elif self.match(TT_RPAREN):
            # () => expr  (zero params)
            self.advance()  # ')'
            if self.match(TT_FATARROW):
                self.advance()  # '=>'
                body = self.parse_expression()
                return LambdaNode([], body)

        # Not a lambda, rewind and parse as grouped expression
        self.pos = saved_pos
        self.advance()  # '('
        expr = self.parse_expression()
        self.expect(TT_RPAREN)
        return expr

    def parse_list(self) -> ListNode:
        """Parse [expr, expr, ...]"""
        self.advance()  # '['
        elements = []
        if not self.match(TT_RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TT_COMMA):
                self.advance()
                if self.match(TT_RBRACKET):
                    break  # trailing comma
                elements.append(self.parse_expression())
        self.expect(TT_RBRACKET)
        return ListNode(elements)

    def parse_take(self) -> TakeNode:
        self.advance()  # 'take'
        self.expect(TT_LPAREN)
        prompt = None
        if not self.match(TT_RPAREN):
            prompt = self.parse_expression()
        self.expect(TT_RPAREN)
        return TakeNode(prompt)

    def parse_call(self, name) -> FunctionCallNode:
        self.expect(TT_LPAREN)
        args = []
        while not self.match(TT_RPAREN):
            args.append(self.parse_expression())
            if self.match(TT_COMMA):
                self.advance()
        self.expect(TT_RPAREN)
        return FunctionCallNode(name, args)

    def parse_builtin_command(self) -> BuiltinCommandNode:
        """Parse &&command — reads identifiers joined by dots as the command name."""
        self.advance()  # consume '&&'
        # Read dotted name: e.g. who.is.eusha
        parts = [self.expect(TT_IDENTIFIER).value]
        while self.match(TT_DOT):
            self.advance()  # '.'
            parts.append(self.expect(TT_IDENTIFIER).value)
        return BuiltinCommandNode('.'.join(parts))

    def parse_fstring(self, parts):
        """Parse interpolated string parts into an FStringNode."""
        from lexer import Lexer as FLexer
        parsed_parts = []
        for kind, value in parts:
            if kind == 'str':
                parsed_parts.append(('str', value))
            elif kind == 'expr':
                # Re-lex and re-parse the expression fragment
                lexer = FLexer(value)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                expr_node = parser.parse_expression()
                parsed_parts.append(('expr', expr_node))
        return FStringNode(parsed_parts)

    def parse_object_literal(self):
        """Parse {key: value, key: value, ...}"""
        self.advance()  # '{'
        self.skip_newlines()
        pairs = []

        # Empty object {}
        if self.match(TT_RBRACE):
            self.advance()
            return ObjectLiteralNode(pairs)

        while True:
            self.skip_newlines()
            # Key can be an identifier or a string
            if self.match(TT_IDENTIFIER) or self.match(TT_KEYWORD):
                key = StringNode(self.advance().value)
            elif self.match(TT_STRING):
                key = StringNode(self.advance().value)
            else:
                raise ParseError(
                    f"Expected a key in object literal, got {self.current().type!r}",
                    self.current().line, self.current().column,
                    "Object keys must be identifiers or strings."
                )
            self.expect(TT_COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            self.skip_newlines()
            if self.match(TT_COMMA):
                self.advance()
                self.skip_newlines()
                if self.match(TT_RBRACE):
                    break  # trailing comma
            else:
                break
        self.expect(TT_RBRACE)
        return ObjectLiteralNode(pairs)
