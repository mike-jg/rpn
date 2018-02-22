from calc import *
import unittest
import io
import sys

class TestLexer(unittest.TestCase):

    def test_empty(self):
        str = ""
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(0, len(tokens))

    def test_simple(self):
        str = "500"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(1, len(tokens))
        self.assertEqual(1, tokens[0].position)
        self.assertEqual(500, tokens[0].lexeme)
        self.assertEqual(Token.NUMBER, tokens[0].type)

    def test_simple2(self):
        str = ".5"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(1, len(tokens))
        self.assertEqual(1, tokens[0].position)
        self.assertEqual(0.5, tokens[0].lexeme)
        self.assertEqual(Token.NUMBER, tokens[0].type)

    def test_float(self):
        str = "7.43424"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(1, len(tokens))
        self.assertEqual(1, tokens[0].position)
        self.assertEqual(7.43424, tokens[0].lexeme)
        self.assertEqual(Token.NUMBER, tokens[0].type)

    def test_func(self):
        str = "sqrt"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(1, len(tokens))
        self.assertEqual(1, tokens[0].position)
        self.assertEqual("sqrt", tokens[0].lexeme)
        self.assertEqual(Token.FUNCTION, tokens[0].type)

    def test_operator(self):
        str = "500 +"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(2, len(tokens))

        self.assertEqual(1, tokens[0].position)
        self.assertEqual(500, tokens[0].lexeme)
        self.assertEqual(Token.NUMBER, tokens[0].type)

        self.assertEqual(5, tokens[1].position)
        self.assertEqual("+", tokens[1].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[1].type)

    def test_all_operators(self):
        str = "+-/*^"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(5, len(tokens))

        self.assertEqual(1, tokens[0].position)
        self.assertEqual("+", tokens[0].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[0].type)

        self.assertEqual(2, tokens[1].position)
        self.assertEqual("-", tokens[1].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[1].type)

        self.assertEqual(3, tokens[2].position)
        self.assertEqual("/", tokens[2].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[2].type)

        self.assertEqual(4, tokens[3].position)
        self.assertEqual("*", tokens[3].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[3].type)

        self.assertEqual(5, tokens[4].position)
        self.assertEqual("^", tokens[4].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[4].type)


    def test_multiple(self):
        str = "1 1 + 2 /   10*"
        lexer = Lexer(str)
        tokens = lexer.tokenize()

        self.assertEqual(7, len(tokens))

        self.assertEqual(1, tokens[0].position)
        self.assertEqual(1, tokens[0].lexeme)
        self.assertEqual(Token.NUMBER, tokens[0].type)

        self.assertEqual(3, tokens[1].position)
        self.assertEqual(1, tokens[1].lexeme)
        self.assertEqual(Token.NUMBER, tokens[1].type)

        self.assertEqual(5, tokens[2].position)
        self.assertEqual("+", tokens[2].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[2].type)

        self.assertEqual(7, tokens[3].position)
        self.assertEqual(2, tokens[3].lexeme)
        self.assertEqual(Token.NUMBER, tokens[3].type)

        self.assertEqual(9, tokens[4].position)
        self.assertEqual("/", tokens[4].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[4].type)

        self.assertEqual(13, tokens[5].position)
        self.assertEqual(10, tokens[5].lexeme)
        self.assertEqual(Token.NUMBER, tokens[5].type)

        self.assertEqual(15, tokens[6].position)
        self.assertEqual("*", tokens[6].lexeme)
        self.assertEqual(Token.OPERATOR, tokens[6].type)


class TestIntegration(unittest.TestCase):

    def test_calc(self):

        tests = [
            ["1.5 1 +", 2.5],
            ["5.35 10.65 +", 16],
            ["1 1 +", 2],
            ["1 2 +", 3],
            ["7 8 * 4 /", 14],
            ["-7 8 +", 1],
            ["-7 5 +8 + +", 6],
            ["-7 5 +8 + + 3", 3],
            ["2 3 11 + 5 -*", 18],
            ["9 5 3 + 2 4 ^ - +", 1],
            ["162 2 1 + 4 ^ /", 2],
            ["6 3 2 ^ - 11 -", -14],
            ["6 3 - 2 ^ 11 -", -2],
            ["2 1 12 3 / - +", -1],
            ["3 2 * 11 -", -5],
        ]

        for t in tests:
            with self.subTest(t=t[0]):
                lexer = Lexer(t[0])
                tokens = lexer.tokenize()
                interpreter = Interpreter(tokens)

                self.assertEqual(t[1], interpreter.interpret())


class TestIntegrationFuncs(unittest.TestCase):

    def test_sqrt(self):

        tests = [
            ["4 4 * sqrt", 4],
            ["625 sqrt", 25],
        ]

        for t in tests:
            with self.subTest(t=t[0]):
                lexer = Lexer(t[0])
                tokens = lexer.tokenize()
                interpreter = Interpreter(tokens)

                self.assertEqual(t[1], interpreter.interpret())

    def test_pop(self):
        tests = [
            ["1 2 3 pop", 2],
            ["5 3 pop", 5],
        ]

        for t in tests:
            with self.subTest(t=t[0]):
                lexer = Lexer(t[0])
                tokens = lexer.tokenize()
                interpreter = Interpreter(tokens)

                self.assertEqual(t[1], interpreter.interpret())

    def test_clear(self):
        tests = [
            ["1 2 3 64 sqrt clear", None],
            ["5 3 clear", None],
        ]

        for t in tests:
            with self.subTest(t=t[0]):
                lexer = Lexer(t[0])
                tokens = lexer.tokenize()
                interpreter = Interpreter(tokens)

                self.assertEqual(t[1], interpreter.interpret())

    def test_print(self):

        tests = [
            ["5 10 * print", "50.0\n"],
            ["1 2 3 64 print", "64.0\n"],
            ["5 print", "5.0\n"],
        ]

        for t in tests:
            with self.subTest(t=t[0]):

                capture = io.StringIO()
                sys.stdout = capture

                lexer = Lexer(t[0])
                tokens = lexer.tokenize()
                interpreter = Interpreter(tokens)

                interpreter.interpret()

                self.assertEqual(t[1], capture.getvalue())

                sys.stdout = sys.__stdout__

    def test_stack(self):

            tests = [
                ["5 10 * stack", "[50.0]\n"],
                ["1 2 3 64 stack", "[1.0, 2.0, 3.0, 64.0]\n"],
                ["5 stack", "[5.0]\n"],
            ]

            for t in tests:
                with self.subTest(t=t[0]):

                    capture = io.StringIO()
                    sys.stdout = capture

                    lexer = Lexer(t[0])
                    tokens = lexer.tokenize()
                    interpreter = Interpreter(tokens)

                    interpreter.interpret()

                    self.assertEqual(t[1], capture.getvalue())

                    sys.stdout = sys.__stdout__


class TestStackError(unittest.TestCase):

    def test_stack_too_short(self):
        with self.assertRaises(InvalidStackError):
            lexer = Lexer("1 /")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

    def test_stack_too_short2(self):
        with self.assertRaises(InvalidStackError):
            lexer = Lexer("1 2 + /")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

    def test_stack_too_short3(self):
        with self.assertRaises(InvalidStackError):
            lexer = Lexer("sqrt")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()


class TestInvalidFunc(unittest.TestCase):

    def test_bad_func1(self):
        with self.assertRaises(InvalidFunctionCallError):
            lexer = Lexer("1 blah")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

    def test_bad_func2(self):
        with self.assertRaises(InvalidFunctionCallError):
            lexer = Lexer("1 2 + 5 / mwauve")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

class TestInvalidChar(unittest.TestCase):

    def test_invalid_char1(self):
        with self.assertRaises(InvalidInputError):
            lexer = Lexer("@")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

    def test_invalid_char2(self):
        with self.assertRaises(InvalidInputError):
            lexer = Lexer("1 2 + 5 / ]")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

    def test_invalid_char3(self):
        with self.assertRaises(InvalidInputError):
            lexer = Lexer("1.1.1.1")
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens)
            interpreter.interpret()

unittest.main()
