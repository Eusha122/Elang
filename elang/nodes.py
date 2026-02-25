
# ============================================================
#  Eusha Language - AST Nodes
# ============================================================

class Node:
    pass

# --- Literals ---
class NumberNode(Node):
    def __init__(self, value):
        self.value = value

class StringNode(Node):
    def __init__(self, value):
        self.value = value

class BoolNode(Node):
    def __init__(self, value: bool):
        self.value = value

class NoneNode(Node):
    pass

# --- Variable ---
class IdentifierNode(Node):
    def __init__(self, name):
        self.name = name

class AssignNode(Node):
    def __init__(self, name, value):
        self.name  = name
        self.value = value

# --- Operations ---
class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right

class UnaryOpNode(Node):
    def __init__(self, op, operand):
        self.op      = op
        self.operand = operand

# --- Say (output) ---
class SayNode(Node):
    """say(expr).newl.tab.space etc."""
    def __init__(self, expr, modifiers: list):
        self.expr      = expr   # expression to print
        self.modifiers = modifiers  # list of strings: 'newl', 'space', 'tab'

# --- Take (input) ---
class TakeNode(Node):
    """take() or take("prompt")"""
    def __init__(self, prompt=None):
        self.prompt = prompt

# --- Type cast method calls ---
class MethodCallNode(Node):
    """expr.method(args)"""
    def __init__(self, obj, method, args=None):
        self.obj    = obj
        self.method = method
        self.args   = args if args is not None else []

# --- If/Else ---
class IfNode(Node):
    def __init__(self, condition, then_block, else_block=None):
        self.condition  = condition
        self.then_block = then_block
        self.else_block = else_block

# --- While ---
class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body      = body

# --- For (range) ---
class ForRangeNode(Node):
    """for (i in start..end step N reverse) { }"""
    def __init__(self, var, start, end, step=None, reverse=False, body=None):
        self.var     = var
        self.start   = start
        self.end     = end
        self.step    = step
        self.reverse = reverse
        self.body    = body

# --- For (each) ---
class ForEachNode(Node):
    """for (x in collection) { }"""
    def __init__(self, var, iterable, body):
        self.var      = var
        self.iterable = iterable
        self.body     = body

# --- Functions ---
class FunctionDefNode(Node):
    def __init__(self, name, params, body, return_type=None):
        self.name        = name
        self.params      = params
        self.body        = body
        self.return_type = return_type

class FunctionCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnNode(Node):
    def __init__(self, value):
        self.value = value

# --- Block ---
class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements

# --- Built-in commands (&&name) ---
class BuiltinCommandNode(Node):
    def __init__(self, command: str):
        self.command = command  # e.g. 'who.is.eusha'

# --- Arrays / Lists ---
class ListNode(Node):
    def __init__(self, elements):
        self.elements = elements

class IndexGetNode(Node):
    def __init__(self, target, index):
        self.target = target
        self.index  = index

class IndexSetNode(Node):
    def __init__(self, target, index, value):
        self.target = target
        self.index  = index
        self.value  = value

# --- Modules ---
class UseNode(Node):
    def __init__(self, module_name):
        self.module_name = module_name

# --- Lambdas ---
class LambdaNode(Node):
    def __init__(self, params, body):
        self.params = params
        self.body   = body

# --- Loop Control Flow ---
class BreakNode(Node):
    pass

class ContinueNode(Node):
    pass

# --- String Interpolation ---
class FStringNode(Node):
    """Interpolated string: "Hello {name}, you are {age}!" """
    def __init__(self, parts):
        self.parts = parts  # list of (type, value): 'str' or 'expr' (Node)

# --- Compound Assignment ---
class CompoundAssignNode(Node):
    """x += 1, x -= 1, etc."""
    def __init__(self, name, op, value):
        self.name  = name
        self.op    = op      # '+', '-', '*', '/'
        self.value = value

# --- Object Literals ---
class ObjectLiteralNode(Node):
    """{key: value, key: value}"""
    def __init__(self, pairs):
        self.pairs = pairs  # list of (key_node, value_node)
