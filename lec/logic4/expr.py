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
    def reducible(self):
        return False
    def collect_vars(self):
        return set()

class Var():
    def __init__(self, name):
        self.name = name
    def get_type(self):
        return ExprType.VAR
    def __str__(self):
        return self.name
    def reducible(self):
        return True
    def reduce(self, evaluation):
        return Const(evaluation[self.name])
    def collect_vars(self):
        return set(self.name)

class Neg():
    def __init__(self, expr):
        self.expr = expr
    def get_type(self):
        return ExprType.NEG
    def __str__(self):
        return f"¬{self.expr}"
    def reducible(self):
        return True
    def reduce(self, evaluation):
        if self.expr.reducible():
            return Neg(self.expr.reduce(evaluation))
        else:
            return Const(not self.expr.value)
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
    def reducible(self):
        return True
    def reduce(self, evaluation):
        if self.left.reducible():
            return Conj(self.left.reduce(evaluation), self.right)
        elif self.right.reducible():
            return Conj(self.left, self.right.reduce(evaluation))
        else:
            return Const(self.left.value and self.right.value)
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
    def reducible(self):
        return True
    def reduce(self, evaluation):
        if self.left.reducible():
            return Disj(self.left.reduce(evaluation), self.right)
        elif self.right.reducible():
            return Disj(self.left, self.right.reduce(evaluation))
        else:
            return Const(self.left.value or self.right.value)
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
    def reducible(self):
        return True
    def reduce(self, evaluation):
        if self.left.reducible():
            return Impl(self.left.reduce(evaluation), self.right)
        elif self.right.reducible():
            return Impl(self.left, self.right.reduce(evaluation))
        else:
            return Const(not(self.left.value) or self.right.value)
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
    def reducible(self):
        return True
    def reduce(self, evaluation):
        if self.left.reducible():
            return Equiv(self.left.reduce(evaluation), self.right)
        elif self.right.reducible():
            return Equiv(self.left, self.right.reduce(evaluation))
        else:
            return Const(not(self.left.value) or self.right.value)
    def collect_vars(self):
        left_vars = self.left.collect_vars()
        right_vars = self.right.collect_vars()
        return left_vars | right_vars  # объединение множеств
