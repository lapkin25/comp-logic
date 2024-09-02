from expr_tree import Parser, ELexerError, EParserError, ExprTreeType, BinaryOperation, NegExprTree, BinaryExprTree, ConstExpr
import sys, io, itertools

f = open('input.txt', 'r')
s = f.readline().strip()
try:
    et = Parser(s).parse()
    et.print(sys.stdout)
    print('')
except EParserError as error:
    print(error.message())
except ELexerError as error:
    print(error.message())


# возвращает множество переменных в формуле
def collect_vars(et):
    if et.get_type() == ExprTreeType.VAR:
        return {et.var_name}
    elif et.get_type() == ExprTreeType.NEG:
        return collect_vars(et.arg)
    elif et.get_type() == ExprTreeType.BIN:
        return collect_vars(et.arg1).union(collect_vars(et.arg2))
    else:
        return {}


# Проверяет, является ли формула тавтологией
def is_tautology(et):
    vars = list(collect_vars(et))
    for vars_values in itertools.product([False, True], repeat=len(vars)):
        if not et.calc(dict(zip(vars, vars_values))):
            return False
    return True


# Возвращает строку со списком гипотез
def hypot_str(hypot):
    s = ""
    start = True
    for h in hypot:
        if not start:
            s = s + ", "
        s = s + get_expr_str(h)
        start = False
    return s


# Добавляет отступы к списку строк
def add_indent(strs):
    for i in range(len(strs)):
        strs[i] = "   " + strs[i]


# Возвращает строку с данным выражением
def get_expr_str(et):
    output = io.StringIO()
    et.print(output)
    text = output.getvalue()
    output.close()
    return text


# совпадают ли два выражения
def equal_exprs(et1, et2):
    if et1.get_type() != et2.get_type():
        return False
    else:
        if et1.get_type() == ExprTreeType.VAR:
            return et1.var_name == et2.var_name
        elif et1.get_type() == ExprTreeType.CONST:
            return et1.const_value == et2.const_value
        elif et1.get_type() == ExprTreeType.NEG:
            return equal_exprs(et1.arg, et2.arg)
        elif et1.get_type() == ExprTreeType.BIN:
            return et1.op == et2.op and equal_exprs(et1.arg1, et2.arg1)\
                   and equal_exprs(et1.arg2, et2.arg2)


# возвращает отрицание заданного выражения
def invert(et):
    if et.get_type() == ExprTreeType.NEG:
        return et.arg.copy_tree()
    else:
        return NegExprTree(et.copy_tree())


# Принимает на вход формулу (типа ExprTree), которую нужно вывести
#   из списка гипотез hypot (список объектов типа ExprTree)
# Возвращает список строк с квазивыводом, список формул с выводом
#   и список строк с пояснением вывода в случае успешного вывода
#   или None, если вывести формулу из гипотез не удалось
def derive(formula, hypot, silent=False):
    # копируем гипотезы в список hyp, который будет пополняться
    hyp = []
    for h in hypot:
        hyp.append(h.copy_tree())

    if not silent:
        if hypot == []:
            proof = ["|- " + get_expr_str(formula)]
        else:
            proof = [hypot_str(hypot) + " |- " + get_expr_str(formula)]
    else:
        proof = []
    detailed_proof = []
    detailed_proof_str = []

    # проверяем, присутствует ли гипотеза среди посылок
    for h in hyp:
        if equal_exprs(formula, h):
            if not silent:
                proof.append("Выводимость очевидна")
            #detailed_proof.append(get_expr_str(h))
            return proof, detailed_proof, detailed_proof_str

    if formula.get_type() == ExprTreeType.NEG:
        # требуется вывести отрицание
        hyp.append(formula.arg.copy_tree())
        formula2 = ConstExpr(False)
        result = derive(formula2, hyp)
        if result is not None:
            proof.append("Сводится к задаче:")
            proof.append("[правило рассуждения от противного]")
            proof1, detailed_proof1, detailed_proof_str1 = result
            add_indent(proof1)
            proof.extend(proof1)

            # Расшифровка правила рассуждения от противного
            detailed_proof = detailed_proof1.copy()
            detailed_proof_str = detailed_proof_str1.copy()
            detailed_proof.append(formula.copy_tree())
            detailed_proof_str.append("A10")

            return proof, detailed_proof, detailed_proof_str

    if formula.get_type() == ExprTreeType.CONST:
        if not formula.const_value:
            # требуется вывести константу 0
            for h1 in hyp:
                for h2 in hyp:
                    if equal_exprs(invert(h1), h2):
                        proof1 = ["0" + "  [" + "из " + get_expr_str(h1) + " и " + get_expr_str(h2) + "]"]
                        #add_indent(proof1)
                        proof.extend(proof1)

                        # Расшифровка вывода противоречия
                        detailed_proof = []
                        detailed_proof_str = []

                        return proof, detailed_proof, detailed_proof_str

    if formula.get_type() == ExprTreeType.BIN:
        if formula.op == BinaryOperation.IMPL:
            # если нужно вывести импликацию,
            #   применяем правило введения импликации
            # (добавляем левую часть импликации к гипотезам
            #   и пытаемся вывести правую часть импликации)
            hyp.append(formula.arg1.copy_tree())
            formula2 = formula.arg2.copy_tree()
            result = derive(formula2, hyp)
            if result is not None:
                proof.append("Сводится к задаче:")
                proof.append("[правило введения импликации]")
                proof1, detailed_proof1, detailed_proof_str1 = result
                add_indent(proof1)
                proof.extend(proof1)

                # Расшифровка правила введения импликации
                #et1 = BinaryExprTree(BinaryOperation.IMPL, formula.arg1.copy_tree(), )
                #detailed_proof.append(BinaryExprTree(BinaryOperation.IMPL),

                detailed_proof = detailed_proof1.copy()
                detailed_proof_str = detailed_proof_str1.copy()
                #detailed_proof.append(formula.copy_tree())
                #detailed_proof_str.append("A10")

                return proof, detailed_proof, detailed_proof_str
        elif formula.op == BinaryOperation.CONJ:
            # если нужно вывести конъюнкцию,
            #   применяем правило введения конъюнкции
            formula1 = formula.arg1.copy_tree()
            formula2 = formula.arg2.copy_tree()
            result1 = derive(formula1, hyp)
            result2 = derive(formula2, hyp)
            if result1 is not None and result2 is not None:
                proof.append("Сводится к задачам:")
                proof.append("[правило введения конъюнкции]")
                proof1, detailed_proof1, detailed_proof_str1 = result1
                add_indent(proof1)
                proof.extend(proof1)
                proof.append("")
                proof2, detailed_proof2, detailed_proof_str2 = result2
                add_indent(proof2)
                proof.extend(proof2)

                # Расшифровка правила введения конъюнкции
                detailed_proof = []
                detailed_proof_str = []

                return proof, detailed_proof, detailed_proof_str
        # elif formula.op == BinaryOperation.DISJ:


    # применение индуктивных действий...

    old_hyp_len = len(hyp)
    detailed_proof = []
    detailed_proof_str = []

    # применяем удаление конъюнкции
    for h in hyp:
        if h.get_type() == ExprTreeType.BIN and h.op == BinaryOperation.CONJ:
            arg1 = h.arg1.copy_tree()
            arg2 = h.arg2.copy_tree()
            hyp1_present = False
            for h1 in hyp:
                if equal_exprs(h1, arg1):
                    hyp1_present = True
                    break
            if not hyp1_present:
                hyp.append(arg1.copy_tree())
            hyp2_present = False
            for h1 in hyp:
                if equal_exprs(h1, arg2):
                    hyp2_present = True
                    break
            if not hyp2_present:
                hyp.append(arg2.copy_tree())
            if not hyp1_present:
                proof.append(get_expr_str(arg1) + "  [" + "правило удаления конъюнкции из " +
                    get_expr_str(h) + "]")
            if not hyp2_present:
                proof.append(get_expr_str(arg2) + "  [" + "правило удаления конъюнкции из " +
                    get_expr_str(h) + "]")

            # Расшифровка правила
            # detailed_proof.append(...)

    # применяем modus ponens
    for h in hyp:
        if h.get_type() == ExprTreeType.BIN and h.op == BinaryOperation.IMPL:
            premise = h.arg1.copy_tree()
            conclusion = h.arg2.copy_tree()
            for h1 in hyp:
                if equal_exprs(h1, premise):
                    # пытаемся добавить conclusion к гипотезам
                    hyp_present = False
                    for h2 in hyp:
                        if equal_exprs(h2, conclusion):
                            hyp_present = True
                            break
                    if not hyp_present:
                        hyp.append(conclusion.copy_tree())
                        proof.append(get_expr_str(conclusion) + "  [" + "modus ponens из " +
                            get_expr_str(h) + " и " + get_expr_str(premise) + "]")
                        #detailed_proof.append(h)
                        #detailed_proof_str.append("")
                        #detailed_proof.append(premise)
                        #detailed_proof_str.append("")
                        detailed_proof.append(conclusion.copy_tree())
                        detailed_proof_str.append("MP из " + get_expr_str(h) + " и " + get_expr_str(premise))

                        # Расшифровка правила modus ponens
                        #detailed_proof = []


    if len(hyp) > old_hyp_len:
        result = derive(formula, hyp, silent=True)
        if result is not None:
            proof1, detailed_proof1, detailed_proof_str1 = result
            #add_indent(proof1)
            proof.extend(proof1)

            return proof, detailed_proof, detailed_proof_str

    return None



if not is_tautology(et):
    print('Формула не является тавтологией')
else:
    result = derive(et, [])
    if result is None:
        print('Вывод не удался')
    else:
        proof, detailed_proof, detailed_proof_str = result
        add_indent(proof)
        proof = ["Задача"] + proof
        for s in proof:
            print(s)
        print('')
        #add_numbers(detailed_proof)
        print("Вывод из аксиом:")
        for i, s in enumerate(detailed_proof):
            print(str(i + 1) + ") ", end='')
            print(get_expr_str(detailed_proof[i]), end='')
            if i > 0:
                print(" ", "[", detailed_proof_str[i], "]")
            else:
                print()

