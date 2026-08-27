from enum import Enum, IntEnum

class ExprType(Enum):
    VAR = 0
    CONST = 1
    NEG = 2
    CONJ = 3
    DISJ = 4
    IMPL = 5
    EQUIV = 6

class Const():
    def __init__(self, value):
        self.value = int(value)
    def get_type(self):
        return ExprType.CONST
    def __str__(self):
        return str(self.value)
    def calc(self, evaluation):
        return self.value
    def collect_vars(self):
        return set()

class Var():
    def __init__(self, name):
        self.name = name
    def get_type(self):
        return ExprType.VAR
    def __str__(self):
        return self.name
    def calc(self, evaluation):
        return evaluation[self.name]
    def collect_vars(self):
        return set(self.name)

class Neg():
    def __init__(self, expr):
        self.expr = expr
    def get_type(self):
        return ExprType.NEG
    def __str__(self):
        return f"¬{self.expr}"
    def calc(self, evaluation):
        return not self.expr.calc(evaluation)
    def collect_vars(self):
        return self.expr.collect_vars()

class Conj():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def get_type(self):
        return ExprType.CONJ
    def __str__(self):
        return f"({self.left} & {self.right})"
    def calc(self, evaluation):
        return self.left.calc(evaluation) and self.right.calc(evaluation)
    def collect_vars(self):
        left_vars = self.left.collect_vars()
        right_vars = self.right.collect_vars()
        return left_vars | right_vars  # объединение множеств

class Disj():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def get_type(self):
        return ExprType.DISJ
    def __str__(self):
        return f"({self.left} ∨ {self.right})"
    def calc(self, evaluation):
        return self.left.calc(evaluation) or self.right.calc(evaluation)
    def collect_vars(self):
        left_vars = self.left.collect_vars()
        right_vars = self.right.collect_vars()
        return left_vars | right_vars  # объединение множеств

class Impl():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def get_type(self):
        return ExprType.IMPL
    def __str__(self):
        return f"({self.left} → {self.right})"
    def calc(self, evaluation):
        return not(self.left.calc(evaluation)) or self.right.calc(evaluation)
    def collect_vars(self):
        left_vars = self.left.collect_vars()
        right_vars = self.right.collect_vars()
        return left_vars | right_vars  # объединение множеств

class Equiv():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def get_type(self):
        return ExprType.EQUIV
    def __str__(self):
        return f"({self.left} ↔ {self.right})"
    def calc(self, evaluation):
        left_value = self.left.calc(evaluation)
        right_value = self.right.calc(evaluation)
        return not left_value and right_value or left_value and not right_value
    def collect_vars(self):
        left_vars = self.left.collect_vars()
        right_vars = self.right.collect_vars()
        return left_vars | right_vars  # объединение множеств
