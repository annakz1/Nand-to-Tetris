from enum import Enum

COMMENT_SYMBOL = '//'
WHITE_SPACE = ' '
EMPTY_STRING = ''
EQUAL_SIGN = '='

CURLY_OPEN = '{'
CURLY_CLOSE = '}'
PARENTHESES_OPEN = '('
PARENTHESES_CLOSE = ')'
SQUARE_BRACKETS_OPEN = '['
SQUARE_BRACKETS_CLOSE = ']'
DOT = '.'
COMMA = ','
SEMICOLON = ';'
PLUS = '+'
MINUS = '-'
ASTERISK = '*'
SLASH = '/'
AMPERSAND = '&amp;'
PIPELINE = '|'
GREATER_THAN = '&gt;'
LESS_THAN = '&lt;'
EQUAL = '='
TILDA = '~'

SYMBOLS_LIST = {CURLY_OPEN, CURLY_CLOSE, PARENTHESES_OPEN, PARENTHESES_CLOSE,
                SQUARE_BRACKETS_OPEN, SQUARE_BRACKETS_CLOSE, DOT, COMMA,
                SEMICOLON, PLUS, MINUS, ASTERISK, SLASH, AMPERSAND, PIPELINE,
                GREATER_THAN, LESS_THAN, EQUAL, TILDA}

CLASS = 'class'
METHOD = 'method'
FUNCTION = 'function'
CONSTRUCTOR = 'constructor'
INT = 'int'
BOOLEAN = 'boolean'
CHAR = 'char'
VOID = 'void'
VAR = 'var'
STATIC = 'static'
FIELD = 'field'
LET = 'let'
DO = 'do'
IF = 'if'
ELSE = 'else'
WHILE = 'while'
RETURN = 'return'
TRUE = 'true'
FALSE = 'false'
NULL = 'null'
THIS = 'this'

KEYWORDS_LIST = {CLASS, METHOD, FUNCTION,
                 CONSTRUCTOR, INT, BOOLEAN,
                 CHAR, VOID, VAR, STATIC,
                 FIELD, LET, DO, IF, ELSE,
                 WHILE, RETURN, TRUE, FALSE,
                 NULL, THIS}


class TokenType(Enum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


class KeywordType(Enum):
    CLASS = 1
    METHOD = 2
    FUNCTION = 3
    CONSTRUCTOR = 4
    INT = 5
    BOOLEAN = 6
    CHAR = 7
    VOID = 8
    VAR = 9
    STATIC = 10
    FIELD = 11
    LET = 12
    DO = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    RETURN = 17
    TRUE = 18
    FALSE = 19
    NULL = 20
    THIS = 21


class JackTokenizer:

    def __init__(self, file_name):
        self.next_word = 0
        self.words = []
        comment_zone = False
        with open(file_name) as jackFile:
            for line in jackFile:
                # cleaning up line
                line = line.strip().split(COMMENT_SYMBOL)[0].strip()
                new_line = ''
                if line:
                    for i in range(len(line)):
                        if i != len(line) - 1:
                            if line[i] == '/' and line[i + 1] == '*':
                                comment_zone = True
                            elif line[i] == '*' and line[i + 1] == '/':
                                comment_zone = False
                        if not comment_zone:
                            if i > 0:
                                if i != len(line) and not (line[i] == '*' and line[i + 1] == '/') and not (
                                        line[i - 1] == '*' and line[i] == '/'):
                                    new_line += line[i]
                            else:
                                if i != len(line) and not (line[i] == '*' and line[i + 1] == '/'):
                                    new_line += line[i]

                    if new_line != '':
                        new_line = new_line.replace(';', ' ; ')
                        new_line = new_line.replace(',', ' , ')
                        new_line = new_line.replace('(', ' ( ')
                        new_line = new_line.replace(')', ' ) ')
                        new_line = new_line.replace('.', ' . ')
                        new_line = new_line.replace('[', ' [ ')
                        new_line = new_line.replace(']', ' ] ')
                        new_line = new_line.replace('}', ' } ')
                        new_line = new_line.replace('{', ' { ')
                        new_line = new_line.replace('-', ' - ')
                        new_line = new_line.replace('~', ' ~ ')
                        new_line = new_line.replace('&', ' &amp; ')
                        new_line = new_line.replace('<', ' &lt; ')
                        new_line = new_line.replace('>', ' &gt; ')

                        new_line_splitted = new_line.split()
                        new_words = []
                        in_string = False
                        build_word = ''
                        for word in new_line_splitted:
                            if '"' in word:
                                if not in_string:
                                    in_string = True
                                    build_word = word
                                else:
                                    in_string = False
                                    build_word += ' ' + word
                                    new_words.append(build_word)
                            else:
                                if not in_string:
                                    new_words.append(word)
                                else:
                                    build_word += ' ' + word
                        self.words.extend(new_words)

    def has_more_tokens(self):
        if len(self.words) > self.next_word:
            return True
        else:
            return False

    def advance(self):
        self.current_token = self.words[self.next_word]
        self.next_word += 1

    def token_type(self):
        if self.current_token in KEYWORDS_LIST:
            return TokenType.KEYWORD
        elif self.current_token in SYMBOLS_LIST:
            return TokenType.SYMBOL
        elif self.is_int(self.current_token):
            return TokenType.INT_CONST
        elif self.current_token.startswith('"'):
            return TokenType.STRING_CONST
        else:
            return TokenType.IDENTIFIER

    def is_int(self, word):
        try:
            int(word)
            return True
        except ValueError:
            return False

    def keyword(self):
        if self.current_token == CLASS:
            return CLASS
        elif self.current_token == CONSTRUCTOR:
            return CONSTRUCTOR
        elif self.current_token == FUNCTION:
            return FUNCTION
        elif self.current_token == METHOD:
            return METHOD
        elif self.current_token == FIELD:
            return FIELD
        elif self.current_token == STATIC:
            return STATIC
        elif self.current_token == VAR:
            return VAR
        elif self.current_token == INT:
            return INT
        elif self.current_token == CHAR:
            return CHAR
        elif self.current_token == BOOLEAN:
            return BOOLEAN
        elif self.current_token == VOID:
            return VOID
        elif self.current_token == TRUE:
            return TRUE
        elif self.current_token == FALSE:
            return FALSE
        elif self.current_token == NULL:
            return NULL
        elif self.current_token == THIS:
            return THIS
        elif self.current_token == LET:
            return LET
        elif self.current_token == DO:
            return DO
        elif self.current_token == IF:
            return IF
        elif self.current_token == ELSE:
            return ELSE
        elif self.current_token == WHILE:
            return WHILE
        elif self.current_token == RETURN:
            return RETURN

    def symbol(self):
        return self.current_token[0]

    def identifier(self):
        return self.current_token

    def int_val(self):
        return int(self.current_token)

    def string_val(self):
        return self.current_token[1:-1]

    def peek_next_token(self):
        return self.words[self.next_word]

