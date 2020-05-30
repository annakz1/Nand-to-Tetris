from enum import Enum

COMMENT_SYMBOL = '//'
PUSH_BEGINNING = 'push'
POP_BEGINNING = 'pop'
ADD_BEGINNING = 'add'
SUBSTRACT_BEGINNING = 'sub'
NEG_BEGINNING = 'neg'
EQUALIZER_BEGINNING = 'eq'
GREATERTHAN_BEGINNING = 'gt'
LOWERTHAN_BEGINNING = 'lt'
AND_BEGINNING = 'and'
OR_BEGINNING = 'or'
NOT_BEGINNING = 'not'
LABEL_BEGINNING = 'label'
GOTO_BEGINNING = 'goto'
IFGOTO_BEGINNING = 'if-goto'
FUNCTION_BEGINNING = 'function'
CALL_BEGINNING = 'call'
RETURN_BEGINNING = 'return'
WHITE_SPACE = ' '
EMPTY_STRING = ''
EQUAL_SIGN = '='
SEMICOLON_SIGN = ';'
ARITHMETIC_LIST = {ADD_BEGINNING, SUBSTRACT_BEGINNING, NEG_BEGINNING,
                   EQUALIZER_BEGINNING, GREATERTHAN_BEGINNING, LOWERTHAN_BEGINNING,
                   AND_BEGINNING, OR_BEGINNING, NOT_BEGINNING}


class CommandType(Enum):
    C_ARITHMETIC = 1
    C_PUSH = 2
    C_POP = 3
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9


class Parser:

    def __init__(self, file_name):
        self.nextLine = 0
        self.linesArray = []
        with open(file_name) as vmFile:
            for line in vmFile:
                # cleaning up line
                line = line.strip().split(COMMENT_SYMBOL)[0]
                if line:
                    self.linesArray.append(line)

    def has_more_lines(self):
        if len(self.linesArray) > self.nextLine:
            return True
        else:
            return False

    def advance(self):
        self.current_command = self.linesArray[self.nextLine]
        self.nextLine += 1

    def instruction_type(self):
        if self.current_command.startswith(tuple(ARITHMETIC_LIST)):
            return CommandType.C_ARITHMETIC
        elif self.current_command.startswith(PUSH_BEGINNING):
            return CommandType.C_PUSH
        elif self.current_command.startswith(POP_BEGINNING):
            return CommandType.C_POP
        elif self.current_command.startswith(LABEL_BEGINNING):
            return CommandType.C_LABEL
        elif self.current_command.startswith(GOTO_BEGINNING):
            return CommandType.C_GOTO
        elif self.current_command.startswith(IFGOTO_BEGINNING):
            return CommandType.C_IF
        elif self.current_command.startswith(FUNCTION_BEGINNING):
            return CommandType.C_FUNCTION
        elif self.current_command.startswith(RETURN_BEGINNING):
            return CommandType.C_RETURN
        elif self.current_command.startswith(CALL_BEGINNING):
            return CommandType.C_CALL

    def arg1(self):
        if self.instruction_type() == CommandType.C_ARITHMETIC:
            return self.current_command
        else:
            return self.current_command.split(WHITE_SPACE)[1]

    # returns dest part
    def arg2(self):
        return self.current_command.split(WHITE_SPACE)[2]
