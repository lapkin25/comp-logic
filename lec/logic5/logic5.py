import itertools
from proof import *


F1 = parse('A -> B')
F2 = parse('B -> C')
F3 = parse('A')
F4 = parse('C')
F5 = parse('B')
rule1 = RuleMP(F1, F3, F5)
rule2 = RuleMP(F5, F2, F4)
proof1 = LinearProof([F1, F2, F3], F4)
proof1.add_line(rule1)
proof1.add_line(rule2)
if not proof1.validate():
    print("Ошибка в доказательстве!")
#proof1.print()
F6 = parse('A -> C')
proof2 = Proof_RuleImplIntro([F1, F2], F6, proof1)
if not proof2.validate():
    print("Ошибка в доказательстве 2!")
#proof2.print()
#print('-' * 30)
#print('Вывод из аксиом:')
#proof2.print_inference()

F7 = Impl(F2, F6)
proof3 = Proof_RuleImplIntro([F1], F7, proof2)
if not proof3.validate():
    print("Ошибка в доказательстве 3!")
proof3.print()
print('-' * 30)
print('Вывод из аксиом:')
proof3.print_inference()


"""
# Построение таблицы истинности...
expr = parse('~x -> y & z')
print(expr)
vars = list(sorted(expr.collect_vars()))  # список переменных формулы
for v in itertools.product([0, 1], repeat=len(vars)):
    eval = dict(zip(vars, v))
    ans = int(expr.calc(eval))
    print(v, '->', ans)
"""
