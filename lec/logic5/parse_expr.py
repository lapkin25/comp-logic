from expr import *
from enum import Enum, IntEnum


class TokenType(Enum):
    EMPTY = 0
    VAR = 1
    CONST = 2
    NEG = 3
    CONJ = 4
    DISJ = 5
    IMPL = 6
    EQUIV = 7
    OPEN_BR = 8
    CLOSE_BR = 9


class Token():
    def token_type(self):
        raise


class EmptyToken(Token):
    def token_type(self):
        return TokenType.EMPTY


class VarToken(Token):
    def token_type(self):
        return TokenType.VAR

    def __init__(self, s, index):
        self.s = s
        self.index = index


class ConstToken(Token):
    def token_type(self):
        return TokenType.CONST

    def __init__(self, val, index):
        self.val = val
        self.index = index


class UnaryOperationToken(Token):
    def token_type(self):
        return TokenType.NEG

    def __init__(self, index):
        self.index = index


class BinaryOperation(IntEnum):
    CONJ = 1
    DISJ = 2
    IMPL = 3
    EQUIV = 4


class BinaryOperationToken(Token):
    def token_type(self):
        return {
            BinaryOperation.CONJ: TokenType.CONJ,
            BinaryOperation.DISJ: TokenType.DISJ,
            BinaryOperation.IMPL: TokenType.IMPL,
            BinaryOperation.EQUIV: TokenType.EQUIV
        }[self.op]

    def __init__(self, op, index):
        self.op = op
        self.index = index


class OpenBracketToken(Token):
    def token_type(self):
        return TokenType.OPEN_BR

    def __init__(self, index):
        self.index = index


class CloseBracketToken(Token):
    def token_type(self):
        return TokenType.CLOSE_BR

    def __init__(self, index):
        self.index = index


class State(Enum):
    START = 0
    LETTER = 1
    DIGIT = 2
    TILDE = 3
    DISJ = 4
    CONJ = 5
    DASH = 6
    LESS = 7
    LESS_DASH = 8
    OPEN_BR = 9
    CLOSE_BR = 10
    DASH_GREATER = 11
    LESS_DASH_GREATER = 12


class ELexerError(Exception):
    def __init__(self, cur, msg):
        self.cur = cur
        self.msg = msg

    def message(self):
        return self.msg + " at position " + str(self.cur + 1)

class EParserError(ELexerError):
    pass

class Lexer():
    def __init__(self, s):
        self.s = s
        self.cur = 0
        self.next_token()

    def next_token(self):
        state = State.START
        letter = None
        digit = None
        index = None  # индекс начала лексемы
        while True:
            if state == State.START:
                if self.cur == len(self.s):
                    self.token = EmptyToken()
                    return
                else:
                    ch = self.s[self.cur]
                    if ch.isalpha():  # если это буква
                        letter = ch
                        index = self.cur
                        state = State.LETTER
                    elif ch == '0' or ch == '1':
                        digit = ch
                        index = self.cur
                        state = State.DIGIT
                    elif ch == '~':
                        index = self.cur
                        state = State.TILDE
                    elif ch == '+' or ch == '|':
                        index = self.cur
                        state = State.DISJ
                    elif ch == '&' or ch == '*':
                        index = self.cur
                        state = State.CONJ
                    elif ch == '=' or ch == '-':
                        index = self.cur
                        state = State.DASH
                    elif ch == '<':
                        index = self.cur
                        state = State.LESS
                    elif ch == '(':
                        index = self.cur
                        state = State.OPEN_BR
                    elif ch == ')':
                        index = self.cur
                        state = State.CLOSE_BR
                    elif ch == ' ':
                        # state = State.START
                        pass
                    else:
                        raise ELexerError(self.cur, "Unexpected symbol")
            elif state == State.LETTER:
                if self.cur == len(self.s) or not self.s[self.cur].isalpha() and not self.s[self.cur].isdigit():
                    self.token = VarToken(letter, index)
                    return
                elif self.s[self.cur].isalpha():
                    raise ELexerError(self.cur, "Extra letter")
                elif self.s[self.cur].isdigit():
                    raise ELexerError(self.cur, "Unexpected digit")
            elif state == State.DIGIT:
                if self.cur == len(self.s) or not self.s[self.cur].isalpha() and not self.s[self.cur].isdigit():
                    self.token = ConstToken(digit == "1", index)
                    return
            elif state == State.TILDE:
                self.token = UnaryOperationToken(index)
                return
            elif state == State.DISJ:
                self.token = BinaryOperationToken(BinaryOperation.DISJ, index)
                return
            elif state == State.CONJ:
                self.token = BinaryOperationToken(BinaryOperation.CONJ, index)
                return
            elif state == State.DASH:
                if self.cur == len(self.s):
                    raise ELexerError(self.cur, "Unexpected end of line")
                elif self.s[self.cur] == '>':
                    state = State.DASH_GREATER
                else:
                    raise ELexerError(self.cur, "Unexpected symbol")
            elif state == State.DASH_GREATER:
                self.token = BinaryOperationToken(BinaryOperation.IMPL, index)
                return
            elif state == State.LESS:
                if self.cur == len(self.s):
                    raise ELexerError(self.cur, "Unexpected end of line")
                elif self.s[self.cur] == '-' or self.s[self.cur] == '=':
                    state = State.LESS_DASH
                else:
                    raise ELexerError(self.cur, "Unexpected symbol")
            elif state == State.LESS_DASH:
                if self.cur == len(self.s):
                    raise ELexerError(self.cur, "Unexpected end of line")
                elif self.s[self.cur] == '>':
                    state = State.LESS_DASH_GREATER
                else:
                    raise ELexerError(self.cur, "Unexpected symbol")
            elif state == State.LESS_DASH_GREATER:
                self.token = BinaryOperationToken(BinaryOperation.EQUIV, index)
                return
            elif state == State.OPEN_BR:
                self.token = OpenBracketToken(index)
                return
            elif state == State.CLOSE_BR:
                self.token = CloseBracketToken(index)
                return

            self.cur = self.cur + 1

    def get_token(self):
        return self.token

    def get_cur(self):
        return self.cur


class Parser():
    def __init__(self, s):
        self.s = s
        self.lexer = Lexer(s)

    def parse(self):
        et = self.parse_equiv()
        if self.lexer.get_token().token_type() != TokenType.EMPTY:
            raise EParserError(self.lexer.get_cur(), "End of expression expected")
        return et

    def parse_equiv(self):
        arg1 = self.parse_impl()
        while self.lexer.get_token().token_type() == TokenType.EQUIV:
            self.lexer.next_token()
            arg2 = self.parse_impl()
            et = Equiv(arg1, arg2)
            arg1 = et
        return arg1

    def parse_impl(self):
        arg1 = self.parse_disj()
        token_type = self.lexer.get_token().token_type()
        if token_type == TokenType.IMPL:
            self.lexer.next_token()
            arg2 = self.parse_impl()
            et = Impl(arg1, arg2)
            # импликация право-ассоциативна: A -> B -> C = A -> (B -> C)
            return et
        else:
            return arg1

    def parse_disj(self):
        arg1 = self.parse_conj()
        while self.lexer.get_token().token_type() == TokenType.DISJ:
            self.lexer.next_token()
            arg2 = self.parse_conj()
            et = Disj(arg1, arg2)
            arg1 = et
        return arg1

    def parse_conj(self):
        arg1 = self.parse_neg()
        while self.lexer.get_token().token_type() == TokenType.CONJ:
            self.lexer.next_token()
            arg2 = self.parse_neg()
            et = Conj(arg1, arg2)
            arg1 = et
        return arg1

    def parse_neg(self):
         if self.lexer.get_token().token_type() == TokenType.NEG:
             self.lexer.next_token()
             arg = self.parse_neg()
             et = Neg(arg)
             return et
         else:
             return self.parse_primary_expr()

    def parse_primary_expr(self):
        token_type = self.lexer.get_token().token_type()
        if token_type == TokenType.OPEN_BR:
            self.lexer.next_token()
            et = self.parse_equiv()
            if self.lexer.get_token().token_type() == TokenType.CLOSE_BR:
                self.lexer.next_token()
                return et
            else:
                raise EParserError(self.lexer.get_cur(), "Closed bracket expected")
        elif token_type == TokenType.CONST:
            const_value = self.lexer.get_token().val
            expr = Const(const_value)
            self.lexer.next_token()
            return expr
        elif token_type == TokenType.VAR:
            var_name = self.lexer.get_token().s
            expr = Var(var_name)
            self.lexer.next_token()
            return expr
        else:
            raise EParserError(self.lexer.get_cur(), "Variable or constant expected")
