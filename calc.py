
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
        self._str = str
        self._pos = 0
        self._tokens = []

    def tokenize(self):
        self._tokens = []

        while not self._is_at_end():
            self._parse_char()

        return self._tokens

    def _parse_char(self):
        char = self._peek()

        if char.isnumeric() or char == ".":
            self._number()

        elif char in "/*^":
            self._operator()

        elif char in "+-":
            self._possible_operator(char)

        elif char.isalpha():
            self._function()

        elif char not in " ":
            raise InvalidInputError(char, self._pos + 1)

        else:
            self._advance()

    def _possible_operator(self, char):
        if char in "-+" and (self._peek1().isnumeric() or self._peek1() == "."):
            self._number()

        else:
            self._operator()

    def _operator(self):
        self._tokens.append(Token(self._peek(), self._pos + 1, Token.OPERATOR))
        self._advance()

    def _peek(self):
        return self._str[self._pos]

    def _peek1(self):
        if self._pos + 1 < len(self._str):
            return self._str[self._pos + 1]
        return ""

    def _advance(self):
        self._pos = self._pos + 1

    def _function(self):
        lexeme = ""
        while not self._is_at_end() and self._peek().isalpha():
            lexeme = lexeme + self._peek()
            self._advance()

        self._tokens.append(Token(lexeme, self._pos - len(lexeme) + 1, Token.FUNCTION))

    def _number(self):
        lexeme = self._peek()
        self._advance()

        found_dot = False

        while not self._is_at_end() and (self._peek().isnumeric() or self._peek() == "."):
            if self._peek() == ".":
                # found two dots in one number, so fail
                if found_dot == True:
                    raise InvalidInputError(self._peek(), self._pos + 1)
                found_dot = True

            lexeme = lexeme + self._peek()
            self._advance()

        num = float(lexeme)

        self._tokens.append(Token(num, self._pos - len(lexeme) + 1, Token.NUMBER))

    def _is_at_end(self):
        return self._pos == len(self._str)

    def __str__(self):
        return "{:d} {:s} '{:s}' {:d}".format(self._pos, str(self._tokens), self._str, len(self._str))

# interpreter executes the commands in the list of tokens
# number literals are added to the stack
# operators and function calls operate on the values contained in the stack
class Interpreter:

    def __init__(self, tokens, stack = None):
        self._tokens = tokens

        # default args accumulate for mutable objects
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if stack is None:
            stack = []
        self._stack = stack
        self.printed = False

        self._func_map = {
                "sqrt": self._sqrt,
                "print": self._print,
                "stack": self._do_stack,
                "pop": self._pop,
                "clear": self._clear
            }

    # interpret the given tokens,
    # returns whatever's left at the top of the stack
    def interpret(self):

        # remember current stack state
        old_stack = self._stack.copy()

        try:
            self._interpret()
        except CalcError as err:
            # reset the stack to the remembered state it was in before the error
            # this gives an opportunity to rerun the same command and fix typos
            # without accidentally messing up the state of the stack
            self._stack.clear()
            self._stack.extend(old_stack)
            raise err

        if len(self._stack) > 0:
            return self._stack[-1]

        return None

    def _interpret(self):

        for token in self._tokens:

            if token.type == Token.OPERATOR:
                self._operator(token)

            elif token.type == Token.NUMBER:
                self._stack.append(token.lexeme)

            elif token.type == Token.FUNCTION:
                self._function(token)

    def _function(self, token):
        func = token.lexeme.lower()
        func_def = self._func_map.get(func, lambda: self._bad_function_call(token))
        func_def()

    def _bad_function_call(self, token):
        raise InvalidFunctionCallError(token)

    def _sqrt(self):
        self._assert_stack_len(1)
        op = self._stack.pop()
        self._stack.append(math.sqrt(abs(op)))

    def _print(self):
        self._assert_stack_len(1)
        print(self._stack[-1])
        self.printed = True

    def _do_stack(self):
        print(self._stack)
        self.printed = True

    def _pop(self):
        self._assert_stack_len(1)
        self._stack.pop()

    def _clear(self):
        self._stack.clear()

    def _operator(self, token):
        self._assert_stack_len(2)
        rightOp = self._stack.pop()
        leftOp = self._stack.pop()

        if token.lexeme == "+":
            self._stack.append(leftOp + rightOp)
        if token.lexeme == "-":
            self._stack.append(leftOp - rightOp)
        if token.lexeme == "/":
            self._stack.append(leftOp / rightOp)
        if token.lexeme == "*":
            self._stack.append(leftOp * rightOp)
        if token.lexeme == "^":
            self._stack.append(math.pow(leftOp, rightOp))

    # check that the stack is of the required length
    # this is because all operations require the stack to be
    # a certain minimum length
    def _assert_stack_len(self, required):
        stacklen = len(self._stack)
        if stacklen < required:
            raise InvalidStackError("Stack is of insufficient length. Length is currently {:d}, a minimum length of {:d} is required.".format(stacklen, required))


if __name__ == "__main__":
    calc()
