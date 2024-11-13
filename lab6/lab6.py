from pycryptosat import Solver
import itertools


s = Solver()

cnf = []


# индекс переменной x_ij
# i, j = 1, 2, 3
# индекс = 1..9
def vind(s, i, j):
    assert(s == 'X' or s == 'O')
    ind = (i - 1) * 3 + j
    if s == 'O':
        ind += 9
    return ind


# добавить дизъюнкт к КНФ
# vlist - список пар (i, j)
def add_clause(vlist):
    l = []
    for p, i, j, r in vlist:
        if r == '+':
            l.append(vind(p, i, j))
        elif r == '-':
            l.append(-vind(p, i, j))
        else:
            raise ValueError("+ or - expected")
    s.add_clause(l)
    cnf.append(l)


def print_cnf(filename):
    with open(filename, 'w') as fout:
        print('p cnf', 18, len(cnf), file=fout)
        for clause in cnf:
            print(" ".join(list(map(str, clause)) + ['0']), file=fout)



inds = range(1, 4)  # индексы клеток

# инициализация игрового поля
field = [['.' for _ in range(0, 4)] for _ in range(0, 4)]

# игровая ситуация
field[1][1] = 'X'
field[1][3] = 'O'
field[2][1] = 'O'
field[3][3] = 'X'

# вывод поля
for i in inds:
    for j in inds:
        print(field[i][j], end='')
    print()

# 1. В одной и той же клетке не может одновременно находиться X и O
for i in inds:
    for j in inds:
        add_clause([('X', i, j, '-'), ('O', i, j, '-')])

# 2. Укажем, какие клетки заняты
for i in inds:
    for j in inds:
        if field[i][j] == 'X':
            add_clause([('X', i, j, '+')])
        elif field[i][j] == 'O':
            add_clause([('O', i, j, '+')])
        elif field[i][j] != '.':
            raise ValueError('Неизвестный символ')

# 3. Ход X производится в одну клетку
for i in inds:
    for j in inds:
        if field[i][j] == '.':
            for k in inds:
                for l in inds:
                    if (i, j) != (k, l) and field[k][l] == '.':
                        add_clause([('X', i, j, '-'), ('X', k, l, '-')])

# 4. В свободных клетках нет O
for i in inds:
    for j in inds:
        if field[i][j] == '.':
            add_clause([('O', i, j, '-')])

# 5. Выигрыш, если три X стоят в одной горизонтали, вертикали или диагонали

# Автоматически приведем условие выигрыша из ДНФ к КНФ
dnf = [[(1, 1), (1, 2), (1, 3)], [(2, 1), (2, 2), (2, 3)], [(3, 1), (3, 2), (3, 3)],
       [(1, 1), (1, 2), (1, 3)], [(1, 2), (2, 2), (3, 2)], [(1, 3), (2, 3), (3, 3)],
       [(1, 1), (2, 2), (3, 3)], [(1, 3), (2, 2), (3, 1)]]
dnf_len = len(dnf)
# генерируем кортежи длины 8 из элементов 0, 1, 2
for seq in itertools.product([0, 1, 2], repeat=dnf_len):
    clause = []
    for p in range(dnf_len):
        i, j = dnf[p][seq[p]]
        clause.append(('X', i, j, '+'))
    add_clause(clause)


print_cnf("cnf.txt")

sat, solution = s.solve()
#print(sat)
#print(solution)

if not sat:
    print('Нет решения')
else:
    new_field = [['.' for _ in range(0, 4)] for _ in range(0, 4)]
    for i in inds:
        for j in inds:
            if solution[vind('X', i, j)]:
                new_field[i][j] = 'X'
            elif solution[vind('O', i, j)]:
                new_field[i][j] = 'O'

    # вывод поля
    print("Решение:")
    for i in inds:
        for j in inds:
            print(new_field[i][j], end='')
        print()
