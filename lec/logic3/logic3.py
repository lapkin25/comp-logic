import itertools
from functools import reduce


class Literal():
    def __init__(self, name, type):
        self.name = name
        assert(type == 'positive' or type == 'negative')
        self.type = type
    def __str__(self):
        if self.type == 'positive':
            return self.name
        else:
            return '¬' + self.name
    def invert(self):
        inv_type = 'negative' if self.type == 'positive' else 'positive'
        lit = Literal(self.name, inv_type)
        return lit
    def calc(self, eval):
        if self.type == 'positive':
            return eval[self.name]
        else:
            return not eval[self.name]

class Disjunct():
    def __init__(self, literals=None):
        if literals is None:
            self.literals = []
        else:
            self.literals = literals
    def __str__(self):
        return ' ∨ '.join(map(str, self.literals))
    def invert(self):
        conj = Conjunct()
        for v in self.literals:
            conj.literals.append(v.invert())
        return conj
    def calc(self, eval):
        return reduce(lambda acc, x: acc or x, map(lambda c: c.calc(eval), self.literals))

class Conjunct():
    def __init__(self, literals=None):
        if literals is None:
            self.literals = []
        else:
            self.literals = literals
    def __str__(self):
        return ' & '.join(map(str, self.literals))
    def invert(self):
        disj = Disjunct()
        for v in self.literals:
            disj.literals.append(v.invert())
        return disj
    def calc(self, eval):
        return reduce(lambda acc, x: acc and x, map(lambda c: c.calc(eval), self.literals))

class CNF():
    def __init__(self, disjuncts=None):
        if disjuncts is None:
            self.disjuncts = []
        else:
            self.disjuncts = disjuncts
    def __str__(self):
        return ' & '.join(map(lambda d: '(' + str(d) + ')', self.disjuncts))
    def invert(self):
        dnf = DNF()
        for disj in self.disjuncts:
            dnf.conjuncts.append(disj.invert())
        return dnf
    def calc(self, eval):
        return reduce(lambda acc, x: acc and x, map(lambda c: c.calc(eval), self.disjuncts))

class DNF():
    def __init__(self, conjuncts=None):
        self.conjuncts = conjuncts if conjuncts is not None else []
    def __str__(self):
        #return ' ∨ '.join(map(str, self.conjuncts))
        return ' ∨ '.join(map(lambda c: '(' + str(c) + ')', self.conjuncts))
    def invert(self):
        cnf = CNF()
        for conj in self.conjuncts:
            cnf.disjuncts.append(conj.invert())
        return cnf
    def calc(self, eval):
        return reduce(lambda acc, x: acc or x, map(lambda c: c.calc(eval), self.conjuncts))

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
    def dnf(self):
        literal = Literal(self.name, "positive")
        conjunct = Conjunct([literal])
        return DNF([conjunct])
    def cnf(self):
        literal = Literal(self.name, "positive")
        disjunct = Disjunct([literal])
        return CNF([disjunct])

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
    def dnf(self):
        #print(self.expr, "=>", self.expr.cnf(), "=>", self.expr.cnf().invert())
        return self.expr.cnf().invert()
    def cnf(self):
        return self.expr.dnf().invert()

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
    def cnf(self):
        left_cnf = self.left.cnf()
        right_cnf = self.right.cnf()
        ans = CNF(left_cnf.disjuncts + right_cnf.disjuncts)
        return ans
    def dnf(self):
        ans = DNF()
        left_dnf = self.left.dnf()
        right_dnf = self.right.dnf()
        for c1 in left_dnf.conjuncts:
            for c2 in right_dnf.conjuncts:
                conjunct = Conjunct(c1.literals + c2.literals)
                ans.conjuncts.append(conjunct)
        return ans

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
    def dnf(self):
        left_dnf = self.left.dnf()
        right_dnf = self.right.dnf()
        ans = DNF(left_dnf.conjuncts + right_dnf.conjuncts)
        return ans
    def cnf(self):
        ans = CNF()
        left_cnf = self.left.cnf()
        right_cnf = self.right.cnf()
        for d1 in left_cnf.disjuncts:
            for d2 in right_cnf.disjuncts:
                disjunct = Disjunct(d1.literals + d2.literals)
                ans.disjuncts.append(disjunct)
        return ans

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
    def dnf(self):
        disj = Disj(Neg(self.left), self.right)
        return disj.dnf()
    def cnf(self):
        disj = Disj(Neg(self.left), self.right)
        return disj.cnf()

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


# пример использования классов
expr = Conj(Impl(Conj(Var('x'), Var('z')), Var('y')), Disj(Neg(Var('y')), Var('z')))
print("Формула:", expr)
dnf = expr.dnf()
cnf = expr.cnf()
print("ДНФ:", dnf)
print("КНФ:", cnf)

print("Проверка...")
print("Значения переменных | Формула | ДНФ | КНФ")
# Построение таблицы истинности...
vars = list(sorted(expr.collect_vars()))  # список переменных формулы
for v in itertools.product([0, 1], repeat=len(vars)):
    eval = dict(zip(vars, v))
    machine = Machine(expr, eval)
    ans = machine.run(verbose=False)
    ans_dnf = int(dnf.calc(eval))
    ans_cnf = int(cnf.calc(eval))
    print(v, ' -> ', ans, ' | ', ans_dnf, ' | ', ans_cnf)
