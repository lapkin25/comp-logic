class Const():
    def __init__(self, value):
        self.value = int(value)
    def __str__(self):
        return str(self.value)
    def reducible(self):
        return False

class Neg():
    def __init__(self, expr):
        self.expr = expr
    def __str__(self):
        return f"¬{self.expr}"
    def reducible(self):
        return True
    def reduce(self):
        if self.expr.reducible():
            return Neg(self.expr.reduce())
        else:
            return Const(not self.expr.value)

class Conj():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} & {self.right})"
    def reducible(self):
        return True
    def reduce(self):
        if self.left.reducible():
            return Conj(self.left.reduce(), self.right)
        elif self.right.reducible():
            return Conj(self.left, self.right.reduce())
        else:
            return Const(self.left.value and self.right.value)

class Disj():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} ∨ {self.right})"
    def reducible(self):
        return True
    def reduce(self):
        if self.left.reducible():
            return Disj(self.left.reduce(), self.right)
        elif self.right.reducible():
            return Disj(self.left, self.right.reduce())
        else:
            return Const(self.left.value or self.right.value)

class Impl():
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} → {self.right})"
    def reducible(self):
        return True
    def reduce(self):
        if self.left.reducible():
            return Impl(self.left.reduce(), self.right)
        elif self.right.reducible():
            return Impl(self.left, self.right.reduce())
        else:
            return Const(not(self.left.value) or self.right.value)

class Machine():
    def __init__(self, expr):
        self.expr = expr
    def step(self):
        self.expr = self.expr.reduce()
    def run(self):
        while self.expr.reducible():
            print(self.expr)
            self.step()
        print(self.expr)


# пример использования классов
expr = Impl(Neg(Disj(Const(1), Const(0))), Conj(Const(0), Const(1)))
#print(expr)
machine = Machine(expr)
machine.run()
