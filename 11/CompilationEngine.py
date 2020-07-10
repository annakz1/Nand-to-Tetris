from JackTokenizer import *
from SymbolTable import IdentifierKind
from VMWriter import Segment

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
BINARY_OPERATORS_TO_FUNC = {ASTERISK: 'call Math.multiply 2',
                            SLASH: 'call Math.divide 2',
                            PLUS: 'add',
                            MINUS: 'sub',
                            AMPERSAND: 'and',
                            PIPELINE: 'or',
                            LESS_THAN: 'lt',
                            GREATER_THAN: 'gt',
                            EQUAL: 'eq'}
UNARY_OPERATORS_TO_FUNC = {TILDA: 'not',
                           MINUS: 'neg'}


class CompilationEngine:
    return_label_counter = 0

    def __init__(self, file_name, more_than_one_file, tokenizer, symbol_table, vm_writer):
        self.output_file = open(file_name + DOT + XML_EXTENSION, "w")
        self.file_name = file_name.split(BACK_SLASH)[-1]
        self.class_name = self.file_name
        self.indent_level = 0
        self.label_index = 0
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
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

    def __write_complete_tag_and_token(self, scope=None, is_used=True):
        tag = self.tokenizer.token_type().name.lower()
        token = self.tokenizer.current_token

        if self.tokenizer.token_type() == TokenType.INT_CONST:
            tag = 'integerConstant'
            self.vm_writer.write_integer_constant(token)
        if self.tokenizer.token_type() == TokenType.STRING_CONST:
            tag = 'stringConstant'
            # TODO self.vm_writer.self.write_string
            token = self.tokenizer.string_val()
        if tag == TokenType.KEYWORD.name.lower():
            keyword = self.tokenizer.keyword()
            if keyword == THIS:
                self.vm_writer.write_push(Segment.POINTER, 0)
            elif keyword == FALSE or keyword == NULL or keyword == TRUE:
                self.vm_writer.write_integer_constant(0)
                if keyword == TRUE:
                    self.vm_writer.write_line('not')

        if tag == TokenType.IDENTIFIER.name.lower():
            self.handle_identifier(tag, token, scope, is_used)
            return

        self.__write_line("<{}> {} </{}>".format(tag, token, tag))

    def __write_line(self, line):
        self.output_file.write(self.__get_indent_string() + line + '\n')

    def __process(self, token, scope=None, is_used=True):
        if self.tokenizer.current_token == token:
            self.__printToken(scope, is_used)
        else:
            print('syntax error, token= ' + token +
                  ', current_token= ' + self.tokenizer.current_token)
        self.tokenizer.advance()

    def __printToken(self, scope=None, is_used=True):
        self.__write_complete_tag_and_token(scope, is_used)

    def compile_class(self):
        self.__write_tag(CLASS)
        self.indent_level += 2
        self.__process(CLASS)
        # process class name
        self.class_name = self.tokenizer.current_token
        self.__process(self.tokenizer.current_token, scope=CLASS, is_used=False)

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current_token in CLASS_VAR_DEC:
                self.__write_tag('classVarDec')
                self.indent_level += 2
                self.compile_var_def(scope=CLASS, is_used=False)
                self.indent_level -= 2
                self.__write_tag('/classVarDec')
            elif self.tokenizer.current_token in SUBROUTINE_DEC:
                subroutine_type = self.tokenizer.current_token
                self.compile_subroutine_dec(subroutine_type)
            else:
                self.__process(self.tokenizer.current_token)

        self.__write_complete_tag_and_token()
        self.indent_level -= 2
        self.__write_tag('/' + CLASS)

    def compile_subroutine_dec(self, subroutine_type):
        self.__write_tag('subroutineDec')
        self.indent_level += 2
        self.symbol_table.start_subroutine()
        # in methods only- argument 0 is always named this
        if subroutine_type == METHOD:
            self.symbol_table.define("this", self.class_name, IdentifierKind.ARG)

        self.__process(self.tokenizer.current_token)
        # process the return value - class name
        self.__process(self.tokenizer.current_token, scope=CLASS, is_used=False)

        subroutine_name = None
        while self.tokenizer.current_token != '}':
            if self.tokenizer.peek_next_token() == "(":
                # process subroutine name- set subroutine identifier
                subroutine_name = self.tokenizer.current_token
                self.__process(self.tokenizer.current_token, scope=SUBROUTINE, is_used=False)
            if self.tokenizer.current_token == '(':
                self.__process(self.tokenizer.current_token)
                self.compile_parameters_list()
                self.__process(self.tokenizer.current_token)
            elif self.tokenizer.current_token == '{':
                self.compile_subroutine_body(subroutine_name)
                break
            else:
                self.__process(self.tokenizer.current_token)

        self.indent_level -= 2
        self.__write_tag('/' + 'subroutineDec')

    def compile_parameters_list(self):
        self.__write_tag('parameterList')
        self.indent_level += 2
        identifier_kind = IdentifierKind.ARG
        identifier_type = self.tokenizer.current_token
        while self.tokenizer.current_token != ')':
            if self.tokenizer.peek_next_token() == "," or self.tokenizer.peek_next_token() == ")":
                # we got to the arg name, add to the symbol table
                self.symbol_table.define(self.tokenizer.current_token, identifier_type, identifier_kind)
            elif self.tokenizer.current_token != ",":
                # we got identifier type
                identifier_type = self.tokenizer.current_token
            self.__process(self.tokenizer.current_token, is_used=False)
        self.indent_level -= 2
        self.__write_tag('/parameterList')

    def compile_subroutine_body(self, subroutine_name):
        self.__write_tag('subroutineBody')
        self.__process(self.tokenizer.current_token)
        self.indent_level += 2

        # check if there are var declarations
        while self.tokenizer.current_token == VAR and self.tokenizer.current_token != '}':
            self.__write_tag('varDec')
            self.indent_level += 2
            self.compile_var_def(scope=SUBROUTINE, is_used=False)
            self.indent_level -= 2
            self.__write_tag('/varDec')

        self.vm_writer.write_function(self.class_name + DOT + subroutine_name,
                                      self.symbol_table.var_count(IdentifierKind.VAR))

        while self.tokenizer.current_token != '}':
            if self.tokenizer.current_token in STATEMENTS_TOKENS:
                self.compile_statements()
            else:
                self.__process(self.tokenizer.current_token)
        self.indent_level -= 2
        self.__process(self.tokenizer.current_token)
        self.__write_tag('/subroutineBody')

    def compile_var_def(self, scope=None, is_used=True):
        identifier_kind = self.get_identifier_kind(self.tokenizer.current_token)
        self.__process(self.tokenizer.current_token)
        # after advance- the token is now the type
        identifier_type = self.tokenizer.current_token
        while self.tokenizer.current_token != ';':
            # if we got to the var name, add to the symbol table
            if self.tokenizer.peek_next_token() == ";" or self.tokenizer.peek_next_token() == ",":
                self.symbol_table.define(self.tokenizer.current_token, identifier_type, identifier_kind)
            self.__process(self.tokenizer.current_token, scope, is_used)
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
        var_name = self.tokenizer.current_token
        self.__process(self.tokenizer.current_token, is_used=False)
        if self.tokenizer.current_token == '[':  # is Array
            self.__process(self.tokenizer.current_token)
            self.compile_expression()
            self.__process(self.tokenizer.current_token)
        else:
            self.__process(EQUAL)
            self.compile_expression()
            kind_of_var = self.symbol_table.kind_of(var_name)
            segment_of_var = self.__get_var_segment_by_kind(kind_of_var)
            index_of_var = self.symbol_table.index_of(var_name)
            self.vm_writer.write_pop(segment_of_var, index_of_var)

        self.__process(SEMICOLON)
        self.indent_level -= 2
        self.__write_tag('/letStatement')

    def compile_if(self):
        self.__write_tag('ifStatement')
        self.indent_level += 2
        self.__process(IF)
        self.__process('(')

        self.compile_expression()
        self.vm_writer.write_line("not")
        if_not_label = self.__get_next_label()
        end_label = self.__get_next_label()
        self.vm_writer.write_if(if_not_label)

        self.__process(')')
        self.__process('{')

        self.compile_statements()
        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(if_not_label)
        self.__process('}')
        if self.tokenizer.current_token == ELSE:
            self.__process('else')
            self.__process('{')
            self.compile_statements()
            self.__process('}')
        self.vm_writer.write_label(end_label)
        self.indent_level -= 2
        self.__write_tag('/ifStatement')

    def __get_next_label(self):
        label = "L" + str(self.label_index)
        self.label_index += 1
        return label

    def compile_while(self):
        self.__write_tag('whileStatement')
        self.indent_level += 2

        while_label = self.__get_next_label()
        end_label = self.__get_next_label()

        self.__process(WHILE)
        self.__process('(')
        self.vm_writer.write_label(while_label)

        self.compile_expression()
        self.vm_writer.write_line('not')
        self.vm_writer.write_if(end_label)

        self.__process(')')
        self.__process('{')
        self.compile_statements()
        self.vm_writer.write_goto(while_label)

        self.vm_writer.write_label(end_label)
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
            if self.tokenizer.peek_next_token() == "(":
                self.__process(self.tokenizer.current_token, scope=SUBROUTINE)
            elif self.tokenizer.peek_next_token() == ".":
                self.invoked_class_name = self.tokenizer.current_token
                self.__process(self.tokenizer.current_token, scope=CLASS, is_used=True)

            else:
                self.__process(self.tokenizer.current_token)

        # the caller of a void method must dump the returned value
        self.vm_writer.write_pop(Segment.TEMP, 0)
        self.tokenizer.advance()
        # self.__process(SEMICOLON)
        self.indent_level -= 2
        self.__write_tag('/doStatement')

    def compile_return(self):
        self.__write_tag('returnStatement')
        self.indent_level += 2
        self.__process(RETURN)
        # check if there's an expression
        if self.tokenizer.current_token != ';':
            self.compile_expression()
        else:
            # returns a value (all methods must return a value)
            self.vm_writer.write_push(Segment.CONST, 0)

        self.vm_writer.write_return()
        self.tokenizer.advance()
        # self.__process(SEMICOLON)
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
                operator = self.tokenizer.current_token
                self.tokenizer.advance()
                self.compile_term()
                self.vm_writer.write_line(UNARY_OPERATORS_TO_FUNC[operator])

            elif self.tokenizer.current_token in OPERATORS:
                operator = self.tokenizer.current_token
                self.tokenizer.advance()
                self.compile_term()
                self.vm_writer.write_line(BINARY_OPERATORS_TO_FUNC[operator])

            else:
                self.__process(self.tokenizer.current_token)

            beginning_expression = False
        self.indent_level -= 2
        self.__write_tag('/expression')

    def compile_expression_list(self):
        num_of_expressions = 0
        self.__write_tag('expressionList')
        self.indent_level += 2
        while self.tokenizer.current_token != ')':
            if self.tokenizer.current_token == ',':
                self.__process(self.tokenizer.current_token)
            num_of_expressions += 1
            self.compile_expression()
        self.indent_level -= 2
        self.__write_tag('/expressionList')
        return num_of_expressions

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
                if self.tokenizer.peek_next_token() == ".":
                    self.invoked_class_name = self.tokenizer.current_token
                    self.__process(self.tokenizer.current_token, scope=CLASS)
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

            if self.tokenizer.peek_next_token() == "(":
                self.__process(self.tokenizer.current_token, scope=SUBROUTINE)
            else:
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
        self.vm_writer.close()

    def get_identifier_kind(self, current_token):
        if current_token == STATIC:
            return IdentifierKind.STATIC
        elif current_token == FIELD:
            return IdentifierKind.FIELD
        elif current_token == VAR:
            return IdentifierKind.VAR

    def handle_identifier(self, tag, identifier_name, scope, is_used):
        identifier_category = self.symbol_table.kind_of(identifier_name)
        identifier_category_str = identifier_category.name.lower()
        if identifier_category == IdentifierKind.NONE:
            identifier_category_str = scope

        token = str(identifier_name) + ";" + str(identifier_category_str) + ";"
        identifier_index = None
        if identifier_category != IdentifierKind.NONE:
            identifier_index = self.symbol_table.index_of(identifier_name)
            token += str(identifier_index) + ";"

        is_used_str = "defined" if is_used == False else "used"
        token += is_used_str
        self.__write_line("<{}> {} </{}>".format(tag, token, tag))

        if identifier_category_str == SUBROUTINE and is_used:  # used subroutine
            n_args = 0
            self.tokenizer.advance()  # move after (
            self.tokenizer.advance()
            n_args += self.compile_expression_list()
            self.vm_writer.write_call(self.invoked_class_name + DOT + identifier_name, n_args)

        elif identifier_category == IdentifierKind.VAR and is_used:
            segment_of_var = self.__get_var_segment_by_kind(identifier_category)
            self.vm_writer.write_push(segment_of_var, identifier_index)

        elif identifier_category == IdentifierKind.ARG and is_used:
            segment_of_var = self.__get_var_segment_by_kind(identifier_category)
            self.vm_writer.write_push(segment_of_var, identifier_index)

    @staticmethod
    def __get_var_segment_by_kind(kind_of_var):
        if kind_of_var == IdentifierKind.STATIC:
            return Segment.STATIC
        elif kind_of_var == IdentifierKind.FIELD:
            return Segment.THIS
        elif kind_of_var == IdentifierKind.ARG:
            return Segment.ARG
        elif kind_of_var == IdentifierKind.VAR:
            return Segment.LOCAL
