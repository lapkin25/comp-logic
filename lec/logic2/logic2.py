import itertools

class Const():
    def __init__(self, value):
        self.value = int(value)
    def __str__(self):
        return str(self.value)
    def reducible(self):
        return False
    def collect_vars(self):
        return set()

class Var():
    def __init__(self, name):
        self.name = name
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

class Machine():
    def __init__(self, expr, evaluation):
        self.expr = expr
        self.evaluation = evaluation
    def step(self):
        self.expr = self.expr.reduce(self.evaluation)
    def run(self, verbose=True):
        while self.expr.reducible():
            if verbose:
                print(self.expr)
            self.step()
        #print(self.expr)
        return self.expr


"""
# пример использования классов
expr = Impl(Neg(Disj(Const(1), Var('y'))), Conj(Const(0), Var('x')))
#print(expr)
eval = {'x': True, 'y': False}
machine = Machine(expr, eval)
machine.run()
"""

# Построение таблицы истинности...
expr = Impl(Neg(Var('x')), Var('y'))  # ввод формулы
print(expr)
vars = list(sorted(expr.collect_vars()))  # список переменных формулы
for v in itertools.product([0, 1], repeat=len(vars)):
    eval = dict(zip(vars, v))
    machine = Machine(expr, eval)
    ans = machine.run(verbose=False)
    print(v, '->', ans)
