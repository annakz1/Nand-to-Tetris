from JackTokenizer import *
from SymbolTable import IdentifierKind

XML_EXTENSION = 'xml'
DOT = '.'
BACK_SLASH = '\\'

SYMBOL = 'symbol'
CLASS_VAR_DEC = {STATIC, FIELD}
SUBROUTINE_DEC = {CONSTRUCTOR, FUNCTION, METHOD}
STATEMENTS_TOKENS = {LET, IF, WHILE, DO, RETURN}
EXPRESSION_ENDING = {';', ')', ']', ','}
TERM_ENDING = {'[', '(', "."}
OPERATORS = {PLUS, MINUS, ASTERISK, SLASH, AMPERSAND,
             PIPELINE, LESS_THAN, GREATER_THAN, EQUAL, TILDA}
UNARY_OPERATORS = {TILDA, MINUS}



class CompilationEngine:
    return_label_counter = 0

    def __init__(self, file_name, more_than_one_file, tokenizer, symbol_table):
        self.output_file = open(file_name + DOT + XML_EXTENSION, "w")
        self.file_name = file_name.split(BACK_SLASH)[-1]
        self.indent_level = 0
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.in_unary = False
        if more_than_one_file:
            pass

    def __get_indent_string(self):
        if self.indent_level == 0:
            return ""
        return " " * self.indent_level

    def set_file_name(self, file_name):
        self.file_name = file_name

    def __write_tag(self, tag):
        self.__write_line("<{}>".format(tag))

    def __write_complete_tag_and_token(self):
        tag = self.tokenizer.token_type().name.lower()
        token = self.tokenizer.current_token

        if self.tokenizer.token_type() == TokenType.INT_CONST:
            tag = 'integerConstant'
        if self.tokenizer.token_type() == TokenType.STRING_CONST:
            tag = 'stringConstant'
            token = self.tokenizer.string_val()
        if tag == TokenType.IDENTIFIER.name.lower():
            self.handle_identifier(tag, token)
            return
        self.__write_line("<{}> {} </{}>".format(tag, token, tag))

    def __write_line(self, line):
        self.output_file.write(self.__get_indent_string() + line + '\n')

    def __process(self, token):
        if self.tokenizer.current_token == token:
            self.__printXMLToken()
        else:
            print('syntax error, token= ' + token +
                  ', current_token= ' + self.tokenizer.current_token)
        self.tokenizer.advance()

    def __printXMLToken(self):
        self.__write_complete_tag_and_token()

    def compile_class(self):
        self.__write_tag(CLASS)
        self.indent_level += 2
        self.__process(CLASS)

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current_token in CLASS_VAR_DEC:
                self.__write_tag('classVarDec')
                self.indent_level += 2
                self.compile_var_def()
                self.indent_level -= 2
                self.__write_tag('/classVarDec')

            elif self.tokenizer.current_token in SUBROUTINE_DEC:
                self.compile_subroutine_dec()
            else:
                self.__process(self.tokenizer.current_token)

        self.__write_complete_tag_and_token()
        self.indent_level -= 2
        self.__write_tag('/' + CLASS)

    def compile_subroutine_dec(self):
        self.__write_tag('subroutineDec')
        self.indent_level += 2
        self.__process(self.tokenizer.current_token)
        while self.tokenizer.current_token != '}':
            if self.tokenizer.current_token == '(':
                self.__process(self.tokenizer.current_token)
                self.compile_parameters_list()
                self.__process(self.tokenizer.current_token)
            elif self.tokenizer.current_token == '{':
                self.compile_subroutine_body()
                break
            else:
                self.__process(self.tokenizer.current_token)

        self.indent_level -= 2
        self.__write_tag('/' + 'subroutineDec')

    def compile_parameters_list(self):
        self.__write_tag('parameterList')
        self.indent_level += 2
        while self.tokenizer.current_token != ')':
            self.__process(self.tokenizer.current_token)
        self.indent_level -= 2
        self.__write_tag('/parameterList')

    def compile_subroutine_body(self):
        self.__write_tag('subroutineBody')
        self.__process(self.tokenizer.current_token)
        self.indent_level += 2
        while self.tokenizer.current_token != '}':
            if self.tokenizer.current_token in STATEMENTS_TOKENS:
                self.compile_statements()
            elif self.tokenizer.current_token == VAR:
                self.__write_tag('varDec')
                self.indent_level += 2
                self.compile_var_def()
                self.indent_level -= 2
                self.__write_tag('/varDec')
            else:
                self.__process(self.tokenizer.current_token)
        self.indent_level -= 2
        self.__process(self.tokenizer.current_token)
        self.__write_tag('/subroutineBody')

    def compile_var_def(self):
        identifier_kind = self.get_identifier_kind(self.tokenizer.current_token)
        self.__process(self.tokenizer.current_token)
        # after advance- the token is now the type
        identifier_type = self.tokenizer.current_token
        while self.tokenizer.current_token != ';':
            # if we got to the var name, add to the symbol table
            if self.tokenizer.peek_next_token() == ";" or self.tokenizer.peek_next_token() == ",":
                self.symbol_table.define(self.tokenizer.current_token, identifier_type, identifier_kind)
            self.__process(self.tokenizer.current_token)
        self.__process(self.tokenizer.current_token)

    def compile_statements(self):
        self.__write_tag('statements')
        self.indent_level += 2
        while self.tokenizer.current_token != '}':
            if self.tokenizer.current_token == LET:
                self.compile_let()
            elif self.tokenizer.current_token == IF:
                self.compile_if()
            elif self.tokenizer.current_token == WHILE:
                self.compile_while()
            elif self.tokenizer.current_token == DO:
                self.compile_do()
            else:
                self.compile_return()
        self.indent_level -= 2
        self.__write_tag('/statements')

    def compile_let(self):
        self.__write_tag('letStatement')
        self.indent_level += 2
        self.__process(LET)
        self.__process(self.tokenizer.current_token)
        if self.tokenizer.current_token == '[':
            self.__process(self.tokenizer.current_token)
            self.compile_expression()
            self.__process(self.tokenizer.current_token)
        self.__process(EQUAL)
        self.compile_expression()
        self.__process(SEMICOLON)
        self.indent_level -= 2
        self.__write_tag('/letStatement')

    def compile_if(self):
        self.__write_tag('ifStatement')
        self.indent_level += 2
        self.__process(IF)
        self.__process('(')
        self.compile_expression()
        self.__process(')')
        self.__process('{')
        self.compile_statements()
        self.__process('}')
        if self.tokenizer.current_token == ELSE:
            self.__process('else')
            self.__process('{')
            self.compile_statements()
            self.__process('}')
        self.indent_level -= 2
        self.__write_tag('/ifStatement')

    def compile_while(self):
        self.__write_tag('whileStatement')
        self.indent_level += 2
        self.__process(WHILE)
        self.__process('(')
        self.compile_expression()
        self.__process(')')
        self.__process('{')
        self.compile_statements()
        self.__process('}')
        self.indent_level -= 2
        self.__write_tag('/whileStatement')

    def compile_do(self):
        self.__write_tag('doStatement')
        self.indent_level += 2
        self.__process('do')
        while self.tokenizer.current_token != ';':
            if self.tokenizer.current_token == '(':
                self.__process(self.tokenizer.current_token)
                self.compile_expression_list()
            self.__process(self.tokenizer.current_token)
        self.__process(SEMICOLON)
        self.indent_level -= 2
        self.__write_tag('/doStatement')

    def compile_return(self):
        self.__write_tag('returnStatement')
        self.indent_level += 2
        self.__process(RETURN)
        while self.tokenizer.current_token != ';':
            self.compile_expression()
        self.__process(SEMICOLON)
        self.indent_level -= 2
        self.__write_tag('/returnStatement')

    def compile_expression(self):
        self.__write_tag('expression')
        self.indent_level += 2
        beginning_expression = True
        while self.tokenizer.current_token not in EXPRESSION_ENDING:
            if self.tokenizer.current_token not in OPERATORS:
                self.compile_term()
                self.in_unary = False
            elif self.tokenizer.current_token in UNARY_OPERATORS and beginning_expression is True:
                self.compile_term()
            else:
                self.__process(self.tokenizer.current_token)
            beginning_expression = False
        self.indent_level -= 2
        self.__write_tag('/expression')

    def compile_expression_list(self):
        self.__write_tag('expressionList')
        self.indent_level += 2
        while self.tokenizer.current_token != ')':
            if self.tokenizer.current_token == ',':
                self.__process(self.tokenizer.current_token)
            self.compile_expression()
        self.indent_level -= 2
        self.__write_tag('/expressionList')

    def compile_term(self):
        self.__write_tag('term')
        self.indent_level += 2
        if self.tokenizer.current_token in UNARY_OPERATORS:
            self.in_unary = True
        else:
            self.in_unary = False
        if self.tokenizer.current_token == '(':
            self.__process(self.tokenizer.current_token)
            self.compile_expression()
            self.__process(self.tokenizer.current_token)
        else:
            if self.tokenizer.current_token == '~':
                self.__process(self.tokenizer.current_token)
                self.compile_term()
            else:
                self.__process(self.tokenizer.current_token)
        while self.tokenizer.current_token in TERM_ENDING:
            if self.tokenizer.current_token == '[':
                self.__process(self.tokenizer.current_token)
                self.compile_expression()
            elif self.tokenizer.current_token == '(':
                self.__process(self.tokenizer.current_token)
                self.compile_expression_list()
            else:  # is dot
                self.__process(self.tokenizer.current_token)
            self.__process(self.tokenizer.current_token)
        if self.tokenizer.current_token in UNARY_OPERATORS and self.in_unary:
            self.compile_expression()
            self.__process(self.tokenizer.current_token)
        if self.in_unary is True:
            self.__write_tag('term')
            self.indent_level += 2
            self.__process(self.tokenizer.current_token)
            self.indent_level -= 2
            self.__write_tag('/term')
            self.in_unary = False
        self.indent_level -= 2
        self.__write_tag('/term')

    def close(self):
        self.output_file.close()

    def get_identifier_kind(self, current_token):
        if current_token == STATIC:
            return IdentifierKind.STATIC
        elif current_token == FIELD:
            return IdentifierKind.FIELD

    def handle_identifier(self, tag, identifier_name):
        identifier_category = self.symbol_table.kind_of(identifier_name)
        token = identifier_name + ";" + identifier_category.name.lower() + ";"
        if identifier_category != IdentifierKind.NONE:
            identifier_index = self.symbol_table.index_of(identifier_name)
            token += str(identifier_index) + ";"

        self.__write_line("<{}> {} </{}>".format(tag, token, tag))


