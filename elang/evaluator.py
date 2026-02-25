
# ============================================================
#  Eusha Language - Evaluator (Tree-walk Interpreter)
# ============================================================

import sys
import os
from nodes import *


# ---- Runtime values ----
class EushaFunction:
    def __init__(self, name, params, body, env, return_type=None):
        self.name        = name
        self.params      = params
        self.body        = body
        self.env         = env   # closure environment
        self.return_type = return_type

    def __repr__(self):
        return f'<fn {self.name}>'


class EushaLambda:
    """Lightweight expression-only lambda."""
    def __init__(self, params, body, env):
        self.params = params
        self.body   = body
        self.env    = env

    def __repr__(self):
        return f'<lambda ({", ".join(self.params)})>'


class EushaModule:
    """Namespace object produced by `use module`."""
    def __init__(self, name, env):
        self.name = name
        self.env  = env   # the module's top-level environment

    def get(self, attr):
        try:
            return self.env.get(attr)
        except RuntimeError_:
            raise RuntimeError_(f"Module '{self.name}' has no attribute '{attr}'")

    def __repr__(self):
        return f'<module {self.name}>'


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class RuntimeError_(Exception):
    def __init__(self, msg, line=0, column=0, hint=""):
        self.msg = msg
        self.line = line
        self.column = column
        self.hint = hint
        super().__init__(f'Runtime Error: {msg}')


# ---- Environment (scope) ----
class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f"Undefined variable '{name}'")

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        """Assign variable in the current scope (local-first)."""
        self.vars[name] = value


# ---- Help Registry ----
HELP_REGISTRY = {
    "say": (
        "  say(expression)\n"
        "  Prints a value. Use modifiers: .newl .space .tab\n"
        "  Example: say(\"Hello\").newl\n"
    ),
    "take": (
        "  take() or take(\"prompt\")\n"
        "  Reads user input. Returns a string.\n"
        "  Example: name = take(\"What is your name? \")\n"
    ),
    "if": (
        "  if condition { ... } else { ... }\n"
        "  Conditional branching.\n"
        "  Example:\n"
        "    if x > 10 {\n"
        "      say(\"big\").newl\n"
        "    } else {\n"
        "      say(\"small\").newl\n"
        "    }\n"
    ),
    "for": (
        "  for (var in start..end) { ... }\n"
        "  for (var in start..end step N) { ... }\n"
        "  for (item in collection) { ... }\n"
        "  Loop over a range or collection.\n"
        "  Example: for (i in 1..5) { say(i).space }\n"
    ),
    "while": (
        "  while (condition) { ... }\n"
        "  Loops as long as condition is true.\n"
        "  Example: while (x < 10) { x = x + 1 }\n"
    ),
    "fn": (
        "  fn name(params) { ... }\n"
        "  Defines a function.\n"
        "  Example:\n"
        "    fn add(a, b) {\n"
        "      return a + b\n"
        "    }\n"
    ),
    "return": (
        "  return expression\n"
        "  Returns a value from a function.\n"
    ),
    "use": (
        "  use module_name\n"
        "  Imports a module as a namespace.\n"
        "  Example: use math\n"
        "           say(math.sqrt(25)).newl\n"
    ),
    "break": (
        "  break\n"
        "  Exits the current loop immediately.\n"
    ),
    "continue": (
        "  continue\n"
        "  Skips to the next iteration of the current loop.\n"
    ),
    "len": (
        "  len(collection)\n"
        "  Returns the length of a list or string.\n"
        "  Example: len([1, 2, 3])  $$ returns 3\n"
    ),
    "help": (
        "  help() or help(\"topic\")\n"
        "  Shows help information.\n"
        "  Available topics: say, take, if, for, while, fn, return,\n"
        "                    use, break, continue, len, help\n"
    ),
}


# ---- Evaluator ----
class Evaluator:
    def __init__(self, source_lines=None, base_path=None):
        self.global_env = Environment()
        self.source_lines = source_lines or []
        self.base_path = base_path or os.getcwd()
        self._setup_builtins()

    def _setup_builtins(self):
        """Register built-in functions into the global environment."""
        # len()
        self.global_env.set('__builtin_len__', True)
        # help()
        self.global_env.set('__builtin_help__', True)

    def eval(self, node: Node, env: Environment):
        method = 'eval_' + type(node).__name__
        fn = getattr(self, method, None)
        if fn is None:
            raise RuntimeError_(f"No evaluator for {type(node).__name__}")
        return fn(node, env)

    # ---- Literals ----
    def eval_NumberNode(self, node, env):
        return node.value

    def eval_StringNode(self, node, env):
        return node.value

    def eval_BoolNode(self, node, env):
        return node.value

    def eval_NoneNode(self, node, env):
        return None

    # ---- Lists ----
    def eval_ListNode(self, node, env):
        return [self.eval(el, env) for el in node.elements]

    # ---- Objects (dicts) ----
    def eval_ObjectLiteralNode(self, node, env):
        obj = {}
        for key_node, val_node in node.pairs:
            key = self.eval(key_node, env)
            val = self.eval(val_node, env)
            obj[key] = val
        return obj

    # ---- F-Strings ----
    def eval_FStringNode(self, node, env):
        parts = []
        for kind, value in node.parts:
            if kind == 'str':
                parts.append(value)
            elif kind == 'expr':
                result = self.eval(value, env)
                parts.append(self._format_value(result))
        return ''.join(parts)

    def eval_IndexGetNode(self, node, env):
        target = self.eval(node.target, env)
        index  = self.eval(node.index, env)
        try:
            if isinstance(target, dict):
                return target[index]
            return target[int(index)]
        except (IndexError, TypeError, KeyError) as e:
            raise RuntimeError_(f"Index error: {e}")

    def eval_IndexSetNode(self, node, env):
        target = self.eval(node.target, env)
        index  = self.eval(node.index, env)
        value  = self.eval(node.value, env)
        try:
            if isinstance(target, dict):
                target[index] = value
            else:
                target[int(index)] = value
            return value
        except (IndexError, TypeError, KeyError) as e:
            raise RuntimeError_(f"Index assignment error: {e}")

    # ---- Variables ----
    def eval_IdentifierNode(self, node, env):
        return env.get(node.name)

    def eval_AssignNode(self, node, env):
        value = self.eval(node.value, env)
        env.assign(node.name, value)
        return value

    # ---- Compound Assignment ----
    def eval_CompoundAssignNode(self, node, env):
        current = env.get(node.name)
        right   = self.eval(node.value, env)
        op = node.op
        try:
            if op == '+':
                if isinstance(current, str) or isinstance(right, str):
                    result = str(current) + str(right)
                else:
                    result = current + right
            elif op == '-': result = current - right
            elif op == '*': result = current * right
            elif op == '/':
                if right == 0:
                    raise RuntimeError_("Division by zero")
                result = current / right
            else:
                raise RuntimeError_(f"Unknown compound operator '{op}'")
        except TypeError as e:
            raise RuntimeError_(str(e))
        env.assign(node.name, result)
        return result

    # ---- Operations ----
    def eval_BinOpNode(self, node, env):
        left  = self.eval(node.left,  env)
        right = self.eval(node.right, env)
        op    = node.op

        try:
            if op == '+':
                # Allow string concatenation
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if op == '-':  return left - right
            if op == '*':  return left * right
            if op == '/':
                if right == 0:
                    raise RuntimeError_("Division by zero")
                return left / right
            if op == '%':  return left % right
            if op == '**': return left ** right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '<':  return left <  right
            if op == '>':  return left >  right
            if op == '<=': return left <= right
            if op == '>=': return left >= right
            if op == 'and': return bool(left) and bool(right)
            if op == 'or':  return bool(left) or  bool(right)
        except TypeError as e:
            raise RuntimeError_(str(e))

        raise RuntimeError_(f"Unknown operator '{op}'")

    def eval_UnaryOpNode(self, node, env):
        val = self.eval(node.operand, env)
        if node.op == '-':   return -val
        if node.op == 'not': return not bool(val)
        raise RuntimeError_(f"Unknown unary op '{node.op}'")

    # ---- say ----
    def eval_SayNode(self, node, env):
        value = self.eval(node.expr, env)
        text  = self._format_value(value)

        # Determine end string from modifiers
        end = ''
        for mod in node.modifiers:
            if mod == 'newl':  end += '\n'
            if mod == 'space': end += ' '
            if mod == 'tab':   end += '\t'

        print(text, end=end, flush=True)
        return None

    def _format_value(self, value):
        """Format a value for display."""
        if value is None:
            return 'none'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, list):
            items = ', '.join(self._format_value(v) for v in value)
            return f'[{items}]'
        if isinstance(value, dict):
            items = ', '.join(f'{self._format_value(k)}: {self._format_value(v)}' for k, v in value.items())
            return '{' + items + '}'
        return str(value)

    # ---- take ----
    def eval_TakeNode(self, node, env):
        prompt = ''
        if node.prompt is not None:
            prompt = str(self.eval(node.prompt, env))
        try:
            return input(prompt)
        except EOFError:
            return ''

    # ---- method calls ----
    def eval_MethodCallNode(self, node, env):
        obj    = self.eval(node.obj, env)
        method = node.method
        args   = [self.eval(a, env) for a in node.args]

        # --- Module namespace access ---
        if isinstance(obj, EushaModule):
            fn = obj.get(method)
            if callable(fn):
                return fn(*args)
            if isinstance(fn, (EushaFunction, EushaLambda)):
                return self._call_function(fn, args)
            if not args:
                return fn
            raise RuntimeError_(f"'{method}' in module '{obj.name}' is not callable")

        # --- Dict/Object methods ---
        if isinstance(obj, dict):
            if method == 'keys':
                return list(obj.keys())
            if method == 'values':
                return list(obj.values())
            if method == 'length':
                return len(obj)
            if method == 'has':
                if len(args) != 1:
                    raise RuntimeError_(".has() takes exactly 1 argument")
                return args[0] in obj
            # Dot-access for dict properties (no parentheses)
            if method in obj and not args:
                return obj[method]
            raise RuntimeError_(f"Unknown object method '.{method}()'")

        # --- Type conversions ---
        try:
            if method == 'to_int':   return int(obj)
            if method == 'to_float': return float(obj)
            if method == 'to_str':   return str(obj)
        except (ValueError, TypeError) as e:
            raise RuntimeError_(f"Cannot convert {obj!r} with .{method}(): {e}")

        # --- List methods ---
        if isinstance(obj, list):
            if method == 'push':
                if len(args) != 1:
                    raise RuntimeError_(".push() takes exactly 1 argument")
                obj.append(args[0])
                return obj
            if method == 'pop':
                if not obj:
                    raise RuntimeError_("Cannot .pop() from an empty list")
                return obj.pop()
            if method == 'sort':
                obj.sort()
                return obj
            if method == 'reverse':
                obj.reverse()
                return obj
            if method == 'sum':
                return sum(obj)
            if method == 'max':
                return max(obj)
            if method == 'min':
                return min(obj)
            if method == 'length':
                return len(obj)
            if method == 'filter':
                if len(args) != 1:
                    raise RuntimeError_(".filter() takes exactly 1 argument (a function)")
                fn = args[0]
                result = []
                for item in obj:
                    val = self._call_function(fn, [item])
                    if bool(val):
                        result.append(item)
                return result
            if method == 'map':
                if len(args) != 1:
                    raise RuntimeError_(".map() takes exactly 1 argument (a function)")
                fn = args[0]
                return [self._call_function(fn, [item]) for item in obj]
            raise RuntimeError_(f"Unknown list method '.{method}()'")

        # --- String methods ---
        if isinstance(obj, str):
            if method == 'length':
                return len(obj)
            if method == 'upper':
                return obj.upper()
            if method == 'lower':
                return obj.lower()
            if method == 'trim':
                return obj.strip()
            if method == 'contains':
                if len(args) != 1:
                    raise RuntimeError_(".contains() takes exactly 1 argument")
                return args[0] in obj
            if method == 'split':
                if len(args) == 0:
                    return obj.split()
                return obj.split(args[0])
            if method == 'replace':
                if len(args) != 2:
                    raise RuntimeError_(".replace() takes exactly 2 arguments")
                return obj.replace(args[0], args[1])
            raise RuntimeError_(f"Unknown string method '.{method}()'")

        raise RuntimeError_(f"Unknown method '.{method}()' on {type(obj).__name__}")

    def _call_function(self, fn, args):
        """Call an EushaFunction or EushaLambda with given arguments."""
        if isinstance(fn, EushaLambda):
            if len(args) != len(fn.params):
                raise RuntimeError_(
                    f"Lambda expects {len(fn.params)} args, got {len(args)}"
                )
            call_env = Environment(parent=fn.env)
            for param, arg in zip(fn.params, args):
                call_env.set(param, arg)
            return self.eval(fn.body, call_env)

        if isinstance(fn, EushaFunction):
            if len(args) != len(fn.params):
                raise RuntimeError_(
                    f"'{fn.name}' expects {len(fn.params)} args, got {len(args)}"
                )
            call_env = Environment(parent=fn.env)
            for param, arg in zip(fn.params, args):
                call_env.set(param, arg)
            try:
                self.eval(fn.body, call_env)
            except ReturnSignal as rs:
                return rs.value
            return None

        raise RuntimeError_(f"Value is not callable")

    # ---- if/else ----
    def eval_IfNode(self, node, env):
        condition = self.eval(node.condition, env)
        if bool(condition):
            return self.eval(node.then_block, env)
        elif node.else_block is not None:
            return self.eval(node.else_block, env)
        return None

    # ---- while ----
    def eval_WhileNode(self, node, env):
        while bool(self.eval(node.condition, env)):
            try:
                self.eval(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
            except ReturnSignal:
                raise
        return None

    # ---- for range ----
    def eval_ForRangeNode(self, node, env):
        start = self.eval(node.start, env)
        end   = self.eval(node.end,   env)
        step  = self.eval(node.step, env) if node.step else 1

        if not isinstance(start, (int, float)):
            raise RuntimeError_("Range start must be a number")
        if not isinstance(end, (int, float)):
            raise RuntimeError_("Range end must be a number")

        start, end, step = int(start), int(end), int(step)

        if node.reverse:
            rng = range(start, end - 1, -abs(step))
        else:
            rng = range(start, end + 1, abs(step))

        for i in rng:
            env.set(node.var, i)
            try:
                self.eval(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
            except ReturnSignal:
                raise
        return None

    # ---- for each ----
    def eval_ForEachNode(self, node, env):
        iterable = self.eval(node.iterable, env)
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError_(f"'{iterable}' is not iterable")
        for item in iterable:
            env.set(node.var, item)
            try:
                self.eval(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
            except ReturnSignal:
                raise
        return None

    # ---- break / continue ----
    def eval_BreakNode(self, node, env):
        raise BreakSignal()

    def eval_ContinueNode(self, node, env):
        raise ContinueSignal()

    # ---- lambdas ----
    def eval_LambdaNode(self, node, env):
        return EushaLambda(node.params, node.body, env)

    # ---- functions ----
    def eval_FunctionDefNode(self, node, env):
        fn = EushaFunction(node.name, node.params, node.body, env, node.return_type)
        env.set(node.name, fn)
        return None

    def eval_FunctionCallNode(self, node, env):
        name = node.name
        args = [self.eval(a, env) for a in node.args]

        # Built-in: len()
        if name == 'len':
            if len(args) != 1:
                raise RuntimeError_("len() takes exactly 1 argument")
            obj = args[0]
            if isinstance(obj, (str, list)):
                return len(obj)
            raise RuntimeError_(f"len() not supported for {type(obj).__name__}")

        # Built-in: help()
        if name == 'help':
            if len(args) == 0:
                print("\n  Elang Help System")
                print("  " + "=" * 30)
                print("  Available topics:")
                for topic in sorted(HELP_REGISTRY.keys()):
                    print(f"    - {topic}")
                print('\n  Usage: help("topic")\n')
                return None
            topic = str(args[0])
            if topic in HELP_REGISTRY:
                print(f"\n  Help: {topic}")
                print("  " + "-" * 30)
                print(HELP_REGISTRY[topic])
                return None
            print(f"\n  No help available for '{topic}'.\n")
            return None

        fn = env.get(name)

        if isinstance(fn, (EushaFunction, EushaLambda)):
            return self._call_function(fn, args)

        raise RuntimeError_(f"'{name}' is not a function")

    def eval_ReturnNode(self, node, env):
        value = self.eval(node.value, env)
        raise ReturnSignal(value)

    # ---- modules (use) ----
    def eval_UseNode(self, node, env):
        module_name = node.module_name

        # Built-in modules
        if module_name == 'math':
            mod_env = Environment()
            import math as pymath
            mod_env.set('pi',    pymath.pi)
            mod_env.set('e',     pymath.e)
            mod_env.set('sqrt',  lambda x: pymath.sqrt(x))
            mod_env.set('abs',   lambda x: abs(x))
            mod_env.set('floor', lambda x: pymath.floor(x))
            mod_env.set('ceil',  lambda x: pymath.ceil(x))
            mod_env.set('round', lambda x: round(x))
            mod_env.set('pow',   lambda x, y: pymath.pow(x, y))
            mod_env.set('sin',   lambda x: pymath.sin(x))
            mod_env.set('cos',   lambda x: pymath.cos(x))
            mod_env.set('tan',   lambda x: pymath.tan(x))
            mod_env.set('log',   lambda x: pymath.log(x))
            module = EushaModule('math', mod_env)
            env.set(module_name, module)
            return None

        if module_name == 'random':
            mod_env = Environment()
            import random as pyrandom
            mod_env.set('randint',  lambda a, b: pyrandom.randint(int(a), int(b)))
            mod_env.set('random',   lambda: pyrandom.random())
            mod_env.set('choice',   lambda lst: pyrandom.choice(lst))
            mod_env.set('shuffle',  lambda lst: (pyrandom.shuffle(lst), lst)[1])
            mod_env.set('uniform',  lambda a, b: pyrandom.uniform(a, b))
            module = EushaModule('random', mod_env)
            env.set(module_name, module)
            return None

        # File-based modules: look for module_name.elang
        module_path = os.path.join(self.base_path, module_name + '.elang')
        if not os.path.exists(module_path):
            # Also check in a 'modules' subfolder
            module_path = os.path.join(self.base_path, 'modules', module_name + '.elang')
        if not os.path.exists(module_path):
            raise RuntimeError_(f"Module '{module_name}' not found")

        with open(module_path, 'r', encoding='utf-8') as f:
            source = f.read()

        from lexer import Lexer
        from parser import Parser

        lexer  = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast    = parser.parse()

        mod_env = Environment()
        mod_evaluator = Evaluator(
            source_lines=source.splitlines(),
            base_path=os.path.dirname(module_path)
        )
        mod_evaluator.global_env = mod_env
        mod_evaluator.eval(ast, mod_env)

        module = EushaModule(module_name, mod_env)
        env.set(module_name, module)
        return None

    # ---- builtin commands (&&cmd) ----
    BUILTIN_COMMANDS = {
        'who.is.eusha': (
            "\n"
            "  Eusha Ibna Akbor\n"
            "\n"
            "  Eusha Ibna Akbor is a 16-year-old programmer from Bangladesh with a strong\n"
            "  foundation in algorithms and software development.\n"
            "\n"
            "  He works on AI-based systems, backend architecture, and programming language\n"
            "  design. His projects focus on clean structure, performance, and thoughtful\n"
            "  engineering decisions.\n"
            "\n"
            "  He is the creator of Elang, a beginner-oriented programming language,\n"
            "  and founder of RareDev.\n"
            "\n"
            "  His interests include systems design, artificial intelligence,\n"
            "  and scalable software engineering.\n"
        ),
    }

    def eval_BuiltinCommandNode(self, node, env):
        cmd = node.command
        if cmd in self.BUILTIN_COMMANDS:
            print(self.BUILTIN_COMMANDS[cmd])
        else:
            print(f'[elang] Unknown command: &&{cmd}')
        return None

    # ---- block ----
    def eval_BlockNode(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.eval(stmt, env)
        return result

    # ---- entry point ----
    def run(self, ast: BlockNode):
        self.eval(ast, self.global_env)
