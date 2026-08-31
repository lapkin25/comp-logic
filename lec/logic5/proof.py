from parse_expr import *

def equal_formulas(formula1, formula2):
    return str(formula1) == str(formula2)

def parse(s):
    return Parser(s).parse()

class Proof:
    def __init__(self, assumptions, conclusion):
        self.assumptions = assumptions  # гипотезы
        self.conclusion = conclusion  # следствие
    def find_assumption(self, expr):
        """
        Найти формулу expr среди гипотез
        """
        for i, formula in enumerate(self.assumptions):
            if equal_formulas(formula, expr):
                return True
        return False
    def inference(self):
        pass
    def print_inference(self):
        inference = self.inference()
        for expr, rule_str, _ in inference:
            print(expr, f'[{rule_str}]')

class LinearProof(Proof):
    def __init__(self, assumptions, conclusion):
        super().__init__(assumptions, conclusion)
        self.lines = []  # строки доказательства
        self.derived_formulas = assumptions.copy()  # список выведенных формул
        self.derived_formulas_numbers = ['Г' + str(i + 1) for i, _ in enumerate(assumptions)]
        self.derived_count = 0
    def find_derived(self, expr):
        """
        Вход: expr - формула, которую ищем в списке выведенных формул
        Выход: индекс найденной формулы либо -1, если такой формулы нет
        """
        for i, formula in enumerate(self.derived_formulas):
            if equal_formulas(formula, expr):
                return i
        return -1
    def add_line(self, rule):
        """
        Добавить строчку доказательства
        """
        # проверяем корректность правила
        for formula in rule.premises:
            if self.find_derived(formula) == -1:
                # в правиле исходные формулы не выведены!
                raise Exception(f"Формула {formula} не выведена!")
        self.lines.append(rule)
        self.derived_formulas.append(rule.conclusion)
        self.derived_count += 1
        self.derived_formulas_numbers.append(str(self.derived_count))
    def validate(self):
        return self.find_derived(self.conclusion) != -1
    def print(self, indentation=0, proof_num=1):
        print(indentation * '  ', end='')
        print(f'(В{proof_num})', ', '.join(map(str, self.assumptions)), '⊢', self.conclusion)
        for i, line in enumerate(self.lines):
            #print(f'({proof_num}.{i + 1})')
            print((indentation + 1) * '  ', end='')
            print(f'/{i + 1}/', line.conclusion, f'[{line.name} {self.premises_str(line)}]')
        print((indentation + 1) * '  ', end='')
        print(f'Вывод (В{proof_num}) построен')
    def premises_str(self, rule):
        formula_numbers = []
        for formula in rule.premises:
            formula_index = self.find_derived(formula)
            formula_number = self.derived_formulas_numbers[formula_index]
            formula_numbers.append(formula_number)
        return ', '.join(formula_numbers)
    def inference(self):
        result = []
        for line in self.lines:
            result += line.inference()
        return result

class RuleMP:
    def __init__(self, premise1, premise2, conclusion):
        # Проверка корректности вывода...
        ok = False
        if premise1.get_type() == ExprType.IMPL and equal_formulas(premise1.left, premise2):
            ok = equal_formulas(conclusion, premise1.right)
        if premise2.get_type() == ExprType.IMPL and equal_formulas(premise2.left, premise1):
            ok = equal_formulas(conclusion, premise2.right)
        if not ok:
            raise Exception("Ошибка в правиле modus ponens")
        self.premises = [premise1, premise2]
        self.conclusion = conclusion
        self.name = 'MP'
    def inference(self):
        return [(self.conclusion, 'MP', self.premises)]

class Proof_RuleImplIntro(Proof):
    def __init__(self, assumptions, conclusion, subproof):
        super().__init__(assumptions, conclusion)
        # Проверка корректности вывода...
        ok = False
        if conclusion.get_type() == ExprType.IMPL:
            if equal_formulas(conclusion.right, subproof.conclusion):
                # остается проверить, что все гипотезы subproof - это либо assumptions, либо левая часть импликации
                ok = True
                for expr in subproof.assumptions:
                    if self.find_assumption(expr) or equal_formulas(expr, conclusion.left):
                        pass
                    else:
                        ok = False
        if not ok:
            raise Exception("Ошибка в правиле введения импликации")
        self.subproof = subproof
        self.name = '→ вв'
    def validate(self):
        return self.subproof.validate()
    def print(self, indentation=0, proof_num=1):
        print(indentation * '  ', end='')
        print(f'(В{proof_num})', ', '.join(map(str, self.assumptions)), '⊢', self.conclusion)
        self.subproof.print(indentation=indentation+1, proof_num=proof_num+1)
        print(indentation * '  ', end='')
        print(f'Вывод (В{proof_num}): [{self.name}] из (В{proof_num + 1})')
    def inference(self):
        # алгоритм из теоремы о дедукции (вывод по квазивыводу)
        result = []
        A = self.conclusion.left
        for expr, rule_str, premises in self.subproof.inference():
            if equal_formulas(expr, A):
                result.append((Impl(A, A), 'Т1', None))
            else:
                implication = Impl(A, expr)
                if self.find_assumption(implication):
                    result.append((implication, 'Г', None))
                else:
                    if premises is not None:
                        premise1 = premises[0]
                        premise2 = premises[1]
                        # TODO: сохранить структуру вывода! чтобы не пришлось ее восстанавливать
                        if premise1.get_type() == ExprType.IMPL and equal_formulas(premise1.left, premise2):
                            B = premise2
                            C = premise1.right
                        if premise2.get_type() == ExprType.IMPL and equal_formulas(premise2.left, premise1):
                            B = premise1
                            C = premise2.right
                        result.append((Impl(Impl(B, C), Impl(A, Impl(B, C))), 'А1', None))
                        result.append((Impl(A, Impl(B, C)), 'MP', [Impl(Impl(B, C), Impl(A, Impl(B, C))), Impl(B, C)]))
                        result.append((Impl(Impl(A, Impl(B, C)), Impl(Impl(A, B), Impl(A, C))), 'А2', None))
                        result.append((Impl(Impl(A, B), Impl(A, C)), 'MP',
                                       [Impl(A, Impl(B, C)), Impl(Impl(A, Impl(B, C)), Impl(Impl(A, B), Impl(A, C)))]))
                        result.append((Impl(A, C), 'MP',
                                       [Impl(Impl(A, B), Impl(A, C)), Impl(A, B)]))
        return result
