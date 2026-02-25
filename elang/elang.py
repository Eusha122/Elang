#!/usr/bin/env python3
# ============================================================
#  Eusha Language - CLI Runner
#  Usage: python elang.py <file.elang>
#         python elang.py (REPL mode)
# ============================================================

import sys
import os

# Make sure we can import sibling modules
sys.path.insert(0, os.path.dirname(__file__))

from lexer     import Lexer, LexerError
from parser    import Parser, ParseError
from evaluator import Evaluator, RuntimeError_

BANNER = """
  ███████╗██╗      █████╗ ███╗   ██╗ ██████╗ 
  ██╔════╝██║     ██╔══██╗████╗  ██║██╔════╝ 
  █████╗  ██║     ███████║██╔██╗ ██║██║  ███╗
  ██╔══╝  ██║     ██╔══██║██║╚██╗██║██║   ██║
  ███████╗███████╗██║  ██║██║ ╚████║╚██████╔╝
  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
  Eusha Language  |  elang v2.0
"""


def format_error(error, source_lines):
    """Format a clean, professional error message with line snippet and pointer."""
    parts = []

    # Get error details
    line_num = getattr(error, 'line', 0)
    column   = getattr(error, 'column', 0)
    msg      = getattr(error, 'msg', str(error))
    hint     = getattr(error, 'hint', '')

    # Error type header
    error_type = type(error).__name__
    if error_type == 'RuntimeError_':
        error_type = 'RuntimeError'
    elif error_type == 'LexerError':
        error_type = 'SyntaxError'
    elif error_type == 'ParseError':
        error_type = 'SyntaxError'

    parts.append(f'\n  {error_type} at line {line_num}:')

    # Show the source line with pointer
    if source_lines and 0 < line_num <= len(source_lines):
        src_line = source_lines[line_num - 1]
        parts.append(f'    {src_line}')
        if column > 0:
            pointer = ' ' * (column - 1 + 4) + '^'
            parts.append(pointer)

    # Error message
    parts.append(f'  {msg}')

    # Hint
    if hint:
        parts.append(f'  Hint: {hint}')

    parts.append('')  # trailing newline
    return '\n'.join(parts)


def run_source(source: str, evaluator: Evaluator, filename='<stdin>') -> bool:
    """Lex → Parse → Eval a source string. Returns True on success."""
    source_lines = source.splitlines()
    evaluator.source_lines = source_lines

    try:
        lexer  = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast    = parser.parse()

        evaluator.run(ast)
        return True

    except (LexerError, ParseError, RuntimeError_) as e:
        print(format_error(e, source_lines), file=sys.stderr)
    except KeyboardInterrupt:
        print('\n  Interrupted.', file=sys.stderr)
    except RecursionError:
        print('\n  RuntimeError: Maximum recursion depth exceeded.', file=sys.stderr)
        print('  Hint: Possible infinite recursion in your code.\n', file=sys.stderr)
    except Exception as e:
        # Suppress Python traceback — show clean message
        print(f'\n  Internal Error: {e}\n', file=sys.stderr)
    return False


def run_file(path: str):
    """Run a .elang file."""
    if not os.path.exists(path):
        print(f'elang: file not found: {path}', file=sys.stderr)
        sys.exit(1)
    if not path.endswith('.elang'):
        print(f'elang: warning: file does not have .elang extension', file=sys.stderr)

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    evaluator = Evaluator(
        source_lines=source.splitlines(),
        base_path=os.path.dirname(os.path.abspath(path))
    )
    success = run_source(source, evaluator, filename=os.path.basename(path))
    sys.exit(0 if success else 1)


def repl():
    """Interactive REPL."""
    print(BANNER)
    print("  Type your Eusha code. Type 'exit' or Ctrl+C to quit.")
    print("  Type help() for documentation.\n")
    evaluator = Evaluator()

    while True:
        try:
            line = input('eusha> ')
        except (EOFError, KeyboardInterrupt):
            print('\nBye!')
            break

        stripped = line.strip()
        if stripped in ('exit', 'quit'):
            print('Bye!')
            break
        if not stripped:
            continue

        run_source(line, evaluator)


def main():
    if len(sys.argv) < 2:
        repl()
    else:
        run_file(sys.argv[1])


if __name__ == '__main__':
    main()
