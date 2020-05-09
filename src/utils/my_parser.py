###
#
# Modified from https://github.com/louisfisch/Mathematical-Expressions-Parser/
#
###

# The MIT License (MIT)

# Copyright (c) 2015 Louis Fischer

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import numpy as np
import h5py

_CONSTANTS = {
    'pi' : math.pi,
    'e' : math.e,
    #'phi': (1 + 5 ** .5) / 2
}

_FUNCTIONS = {
    'abs': abs,
    'arccos': np.arccos,
    'arcsin': np.arcsin,
    'arctan': np.arctan,
    'arctan2': np.arctan2,
    'ceil': np.ceil,
    'cos': np.cos,
    'cosh': np.cosh,
    'exp': np.exp,
    'fabs': np.fabs,
    'floor': np.floor,
    'log': np.log,
    'log10': np.log10,
    'pow': np.power,
    'sin': np.sin,
    'sinh': np.sinh,
    'append': np.append,
    'sum': np.sum,
    'take': np.take,
    'average': np.average,
    'sqrt': np.sqrt,
    'tan': np.tan,
    'tanh': np.tanh
}

def h5_getter(filepath, attribute, prtl_stride=None):
    with h5py.File(filepath, 'r') as f:
        if prtl_stride is not None:
            return f[attribute][::prtl_stride]
        else:
            return f[attribute][:]
class ExprParser:
    def __init__(self, string='', vars=None):
        self.__string = string
        self.index = 0
        self.__vars = {}
        self.vars = vars
        self.f_end = ''

    def getValue(self, expr=None):
        if not expr is None:
            self.string = expr
        value = self.parseExpression()
        self.skipWhitespace()

        if self.hasNext():
            raise Exception(
                "Unexpected character found: '" + self.peek() + "' at index " + str(self.index)
            )
        return value

    @property
    def vars(self):
        return self.__vars

    @vars.setter
    def vars(self, vars_dict=None):
        self.__vars = {} if vars_dict == None else vars_dict.copy()
        for constant in _CONSTANTS.keys():
            if self.vars.get(constant) != None:
                raise Exception("Cannot redefine the value of " + constant)

    @property
    def string(self):
        return self.__string

    @string.setter
    def string(self, expr):
        self.__string = expr
        self.index = 0

    def peek(self):
        return self.string[self.index:self.index + 1]

    def hasNext(self):
        return self.index < len(self.string)

    def isNext(self, value):
        return self.string[self.index:self.index+len(value)] == value

    def popIfNext(self, value):
        if self.isNext(value):
            self.index += len(value)
            return True
        return False

    def popExpected(self, value):
        if not self.popIfNext(value):
            raise Exception("Expected '" + value + "' at index " + str(self.index))


    def skipWhitespace(self):
        while self.hasNext():
            if self.peek() in ' \t\n\r':
                self.index += 1
            else:
                return

    def parseExpression(self):
        return self.parseAddition()

    def parseAddition(self):
        values = [self.parseMultiplication()]

        while True:
            self.skipWhitespace()
            char = self.peek()

            if char == '+':
                self.index += 1
                values.append(self.parseMultiplication())
            elif char == '-':
                self.index += 1
                values.append(-1 * self.parseMultiplication())
            else:
                break

        return sum(values)

    def parseMultiplication(self):
        values = [self.parseParenthesis()]

        while True:
            self.skipWhitespace()
            char = self.peek()

            if char == '*':
                self.index += 1
                values.append(self.parseParenthesis())
            elif char == '/':
                div_index = self.index
                self.index += 1
                denominator = self.parseParenthesis()

                if denominator == 0:
                    raise Exception(
                        "Division by 0 (occured at index " + str(div_index) + ")"
                    )
                values.append(1.0 / denominator)
            else:
                break

        value = 1.0

        for factor in values:
            value *= factor
        return value

    def parseParenthesis(self):
        self.skipWhitespace()
        char = self.peek()

        if char == '(':
            self.index += 1
            value = self.parseExpression()
            self.skipWhitespace()

            if self.peek() != ')':
                raise Exception(
                    "No closing parenthesis found at character " + str(self.index)
                )
            self.index += 1
            return value
        else:
            return self.parseNegative()

    def parseArguments(self):
        args = []
        self.skipWhitespace()
        self.popExpected('(')
        while not self.popIfNext(')'):
            self.skipWhitespace()
            if len(args) > 0:
                self.popExpected(',')
                self.skipWhitespace()
            args.append(self.parseExpression())
            self.skipWhitespace()
        return args

    def parseNegative(self):
        self.skipWhitespace()
        char = self.peek()

        if char == '-':
            self.index += 1
            return -1 * self.parseParenthesis()
        else:
            return self.parseValue()

    def parseValue(self):
        self.skipWhitespace()
        char = self.peek()

        if char in '0123456789.':
            return self.parseNumber()
        else:
            return self.parseVariable()

    def parseVariable(self):
        self.skipWhitespace()
        var = []
        while self.hasNext():
            char = self.peek()

            if char.lower() in '_abcdefghijklmnopqrstuvwxyz0123456789':
                var.append(char)
                self.index += 1
            else:
                break
        var = ''.join(var)

        function = _FUNCTIONS.get(var.lower())
        if function != None:
            args = self.parseArguments()
            return function(*args)

        constant = _CONSTANTS.get(var.lower())
        if constant != None:
            return constant

        fpath = self.vars.get(var, None)
        value = h5_getter(fpath+self.f_end, var)

        if len(value) > 0:
            return value

        raise Exception("Unrecognized variable: '" + var + "'")

    def parseNumber(self):
        self.skipWhitespace()
        strValue = ''
        decimal_found = False
        char = ''

        while self.hasNext():
            char = self.peek()

            if char == '.':
                if decimal_found:
                    raise Exception(
                        "Found an extra period in a number at character " + str(self.index) + ". Are you European?"
                    )
                decimal_found = True
                strValue += '.'
            elif char in '0123456789':
                strValue += char
            else:
                break
            self.index += 1

        if len(strValue) == 0:
            if char == '':
                raise Exception("Unexpected end found")
            else:
                raise Exception(
                    "I was expecting to find a number at character " + str(self.index) + " but instead I found a '" + char + "'. What's up with that?")

        return float(strValue)

def evaluate(expression, vars = None):
    try:
        p = ExprParser(expression, vars)
        value = p.getValue()
    except Exception as ex:
        raise Exception



    return value

if __name__ == "__main__":
    # assert np.abs(evaluate("cos(take(x,0)+4*3) + 2 * 3 - y", { 'x': np.linspace(0,np.pi,num = 100), 'y':10 }) - np.cos(12) +4) <1E-8
    # assert evaluate("exp(0)") == 1
    # assert evaluate("-(1 + 2) * 3") == -9
    print(evaluate("(1-2)/3.0 + 0.0000"))
    print(evaluate("abs(-2) + pi / 4"))
    # print(evaluate("(x + e * 10) / 10", { 'x' : 3 }))
    print(evaluate("1.0 / 3 * 6"))
    print(evaluate("(1 - 1 + -1) * pi"))
    print(evaluate("cos(pi) * 1"))
    print(evaluate("arctan2(2, 1)"))
    print(evaluate("pow(3, 5)"))
