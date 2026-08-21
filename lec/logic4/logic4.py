import itertools
from parse_expr import *


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


exprs = []
f = open('input.txt', 'r')
for s1 in f.readlines():
    s = s1.strip()
    try:
        expr = Parser(s).parse()
        #print(expr)
        exprs.append(expr)
    except EParserError as error:
        print(error.message())
        exit()
    except ELexerError as error:
        print(error.message())
        exit()

hypot = exprs[:-1]
conseq = exprs[-1]

print("Гипотезы:")
print('\n'.join(map(str, hypot)))
print("Следствие:")
print(conseq)

print("Критерий логического следствия:")
criterion = hypot[0]
for i in range(1, len(hypot)):
    criterion = Conj(criterion, hypot[i])
criterion = Impl(criterion, conseq)

print(criterion)
# Построение таблицы истинности...
print("Таблица истинности:")
vars = list(sorted(criterion.collect_vars()))  # список переменных формулы
for v in itertools.product([0, 1], repeat=len(vars)):
    eval = dict(zip(vars, v))
    machine = Machine(criterion, eval)
    ans = machine.run(verbose=False)
    print(v, '->', ans)
