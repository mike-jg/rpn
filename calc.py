
import math

def calc():
    stack = []
    while True:
        inputStr = input("> ")
        if inputStr in ["q", ":q", "quit", "exit"]:
            break

        try:

            lexer = Lexer(inputStr)
            tokens = lexer.tokenize()
            interpreter = Interpreter(tokens, stack)
            result = interpreter.interpret()

            # don't print anything if the interpreter
            # already ran a print command, otherwise
            # the output looks a bit confusing
            if not interpreter.printed:
                print(result)

        except InvalidInputError as err:
            print((" " * (err.position + 1)) + "^")
            print("Invalid character '{:s}'".format(err.char))

        except InvalidFunctionCallError as err:
            print((" " * (err.token.position + 1)) + ("^" * len(err.token.lexeme)))
            print("Invalid function call '{:s}'".format(err.token.lexeme))

        except InvalidStackError as err:
            print(err.message)

# base exception for calc exceptions
class CalcError(Exception):
    pass

# stack is not in a valid state for the request operation
# e.g. not enough arguments on it
class InvalidStackError(CalcError):
    def __init__(self, message):
        self.message = message

# some invalid input was provided, e.g. invalid characters
class InvalidInputError(CalcError):
    def __init__(self, char, position):
        self.char = char
        self.position = position

# non existent function was called
class InvalidFunctionCallError(CalcError):
    def __init__(self, token):
        self.token = token

# a token is the smallest sequence of chars that mean something
# e.g. sqrt is a function call
# e.g. 5 is a number literal
class Token:

    # binary operator such as + or -
    OPERATOR = "operator"
    # number literal
    NUMBER = "number"
    # function call
    FUNCTION = "function"

    def __init__(self, lexeme, position, type):
        self.lexeme = lexeme
        self.position = position
        self.type = type

    def __str__(self):
        return "Token {:s} {:d} {:s}".format(self.lexeme, str(self.position), self.type)

# the Lexer converts the input into a list of tokens
class Lexer:
    def __init__(self, str):
        self.str = str
        self.pos = 0
        self.tokens = []

    def tokenize(self):
        self.tokens = []

        while not self.is_at_end():
            self.parse_char()

        return self.tokens

    def parse_char(self):
        char = self.peek()

        if char.isnumeric() or char == ".":
            self.number()

        elif char in "+-/*^":
            self.possible_operator(char)

        elif char.isalpha():
            self.function()

        elif char not in " ":
            raise InvalidInputError(char, self.pos + 1)

        else:
            self.advance()

    def possible_operator(self, char):
        if char in "-+" and (self.peek1().isnumeric() or self.peek1() == "."):
            self.number()

        else:
            self.tokens.append(Token(char, self.pos + 1, Token.OPERATOR))
            self.advance()

    def peek(self):
        return self.str[self.pos]

    def peek1(self):
        if self.pos + 1 < len(self.str):
            return self.str[self.pos + 1]
        return ""

    def advance(self):
        self.pos = self.pos + 1

    def function(self):
        lexeme = ""
        while not self.is_at_end() and self.peek().isalpha():
            lexeme = lexeme + self.peek()
            self.advance()

        self.tokens.append(Token(lexeme, self.pos - len(lexeme) + 1, Token.FUNCTION))

    def number(self):
        lexeme = ""
        negative = self.peek() == "-"
        if (negative or self.peek() == "+"):
            self.advance()

        found_dot = False

        while not self.is_at_end() and (self.peek().isnumeric() or self.peek() == "."):
            if self.peek() == ".":
                # found two dots in one number, so fail
                if found_dot == True:
                    raise InvalidInputError(self.peek(), self.pos + 1)
                found_dot = True

            lexeme = lexeme + self.peek()
            self.advance()

        num = float(lexeme)
        if negative:
            num = -num

        self.tokens.append(Token(num, self.pos - len(lexeme) + 1, Token.NUMBER))

    def is_at_end(self):
        return self.pos == len(self.str)

    def __str__(self):
        return "{:d} {:s} '{:s}' {:d}".format(self.pos, str(self.tokens), self.str, len(self.str))

# interpreter executes the commands in the list of tokens
# number literals are added to the stack
# operators and function calls operate on the values contained in the stack
class Interpreter:

    def __init__(self, tokens, stack = None):
        self.tokens = tokens

        # default args accumulate for mutable objects
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if stack is None:
            stack = []
        self.stack = stack
        self.printed = False

    def interpret(self):

        # remember current stack state
        old_stack = self.stack.copy()

        try:
            self.do_interpret()
        except CalcError as err:
            # reset the stack to the remembered state it was in before the error
            # this gives an opportunity to rerun the same command and fix typos
            # without accidentally messing up the state of the stack
            self.stack.clear()
            self.stack.extend(old_stack)
            raise err

        if len(self.stack) > 0:
            return self.stack[-1]

        return None

    def do_interpret(self):
        for token in self.tokens:

            if token.type == Token.OPERATOR:
                self.operator(token)

            elif token.type == Token.NUMBER:
                self.stack.append(token.lexeme)

            elif token.type == Token.FUNCTION:
                self.function(token)

    def function(self, token):
        func = token.lexeme.lower();

        if func == "sqrt":
            self.assert_stack_len(1)
            op = self.stack.pop()
            self.stack.append(math.sqrt(abs(op)))

        elif func == "print":
            self.assert_stack_len(1)
            print(self.stack[-1])
            self.printed = True

        elif func == "stack":
            print(self.stack)
            self.printed = True

        elif func == "pop":
            self.assert_stack_len(1)
            self.stack.pop()

        elif func == "clear":
            self.stack.clear()

        else:
            raise InvalidFunctionCallError(token)

    def operator(self, token):
        self.assert_stack_len(2)
        rightOp = self.stack.pop()
        leftOp = self.stack.pop()

        if token.lexeme == "+":
            self.stack.append(leftOp + rightOp)
        if token.lexeme == "-":
            self.stack.append(leftOp - rightOp)
        if token.lexeme == "/":
            self.stack.append(leftOp / rightOp)
        if token.lexeme == "*":
            self.stack.append(leftOp * rightOp)
        if token.lexeme == "^":
            self.stack.append(math.pow(leftOp, rightOp))

    # check that the stack is of the required length
    # this is because all operations require the stack to be
    # a certain minimum length
    def assert_stack_len(self, required):
        stacklen = len(self.stack)
        if stacklen < required:
            raise InvalidStackError("Stack is of insufficient length. Length is currently {:d}, a minimum length of {:d} is required.".format(stacklen, required))


if __name__ == "__main__":
    calc()
