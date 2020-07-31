from JackTokenizer import *
from SymbolTable import IdentifierKind
from VMWriter import Segment

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

    def __init__(self, file_name, more_than_one_file, tokenizer, symbol_table, vm_writer, label_index):
        self.file_name = file_name.split(BACK_SLASH)[-1]
        self.class_name = self.file_name
        self.label_index = label_index
        self.invoked_arg_count = 0
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
        self.in_unary = False
        self.is_array_var = False
        self.is_method_invocation = True
        if more_than_one_file:
            pass

    def set_file_name(self, file_name):
        self.file_name = file_name

    def __write_complete_tag_and_token(self, scope=None, is_used=True):
        tag = self.tokenizer.token_type().name.lower()
        token = self.tokenizer.current_token

        if self.tokenizer.token_type() == TokenType.INT_CONST:
            tag = 'integerConstant'
            self.vm_writer.write_integer_constant(token)
        if self.tokenizer.token_type() == TokenType.STRING_CONST:
            tag = 'stringConstant'
            token = self.tokenizer.string_val()
            self.vm_writer.write_string_constant(token)
        if tag == TokenType.KEYWORD.name.lower():
            keyword = self.tokenizer.keyword()
            if keyword == THIS:
                # sets the base address of the new object
                self.vm_writer.write_push(Segment.POINTER, 0)
            elif keyword == FALSE or keyword == NULL or keyword == TRUE:
                self.vm_writer.write_integer_constant(0)
                if keyword == TRUE:
                    self.vm_writer.write_line('not')

        if tag == TokenType.IDENTIFIER.name.lower():
            self.handle_identifier(tag, token, scope, is_used)
            return

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
        self.__process(CLASS)
        # process class name
        self.class_name = self.tokenizer.current_token
        self.__process(self.tokenizer.current_token, scope=CLASS, is_used=False)

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current_token in CLASS_VAR_DEC:
                self.compile_var_def(scope=CLASS, is_used=False)
            elif self.tokenizer.current_token in SUBROUTINE_DEC:
                subroutine_type = self.tokenizer.current_token
                self.compile_subroutine_dec(subroutine_type)
            else:
                self.__process(self.tokenizer.current_token)

        self.__write_complete_tag_and_token()

    def compile_subroutine_dec(self, subroutine_type):
        # creates the subroutine’s symbol table
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
                self.compile_subroutine_body(subroutine_name, subroutine_type)
                break
            else:
                self.__process(self.tokenizer.current_token)


    def compile_parameters_list(self):
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

    def compile_subroutine_body(self, subroutine_name, subroutine_type):
        self.__process(self.tokenizer.current_token)

        # check if there are var declarations
        while self.tokenizer.current_token == VAR and self.tokenizer.current_token != '}':
            self.compile_var_def(scope=SUBROUTINE, is_used=False)

        self.vm_writer.write_function(self.class_name + DOT + subroutine_name,
                                      self.symbol_table.var_count(IdentifierKind.VAR))

        if subroutine_type == CONSTRUCTOR:
            self.invoked_class_name = self.class_name
            # creating a memory block for representing the new object
            self.vm_writer.write_integer_constant(self.symbol_table.var_count(IdentifierKind.FIELD))
            self.vm_writer.write_call('Memory.alloc', 1)
            # anchors THIS at the base address
            self.vm_writer.write_pop(Segment.POINTER, 0)
        elif subroutine_type == METHOD:
            # generates code that associates the 'this' memory segment with the object on
            # which the method was called to operate
            self.vm_writer.write_push(Segment.ARG, 0)
            self.vm_writer.write_pop(Segment.POINTER, 0)  # THIS = argument 0

        while self.tokenizer.current_token != '}':
            if self.tokenizer.current_token in STATEMENTS_TOKENS:
                self.compile_statements()
            else:
                self.__process(self.tokenizer.current_token)
        self.__process(self.tokenizer.current_token)  # self.tokenizer.advance() # }

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

    def compile_let(self):
        self.__process(LET)
        var_name = self.tokenizer.current_token
        self.__process(self.tokenizer.current_token, is_used=False)
        if self.tokenizer.current_token == '[':  # is Array
            self.__process(self.tokenizer.current_token)
            self.compile_expression()
            self.__process(self.tokenizer.current_token)

            segment_of_var, index_of_var = self.__get_segment_and_index_of_var(var_name)
            self.vm_writer.write_push(segment_of_var, index_of_var)

            self.vm_writer.write_line('add')
            self.tokenizer.advance()  # move after =
            self.compile_expression()

            self.vm_writer.write_pop(Segment.TEMP, 0)  # temp 0 = the value of expression2
            self.vm_writer.write_pop(Segment.POINTER, 1)
            self.vm_writer.write_push(Segment.TEMP, 0)
            self.vm_writer.write_pop(Segment.THAT, 0)  # save in original var

        else:
            self.__process(EQUAL)
            self.compile_expression()
            segment_of_var, index_of_var = self.__get_segment_and_index_of_var(var_name)

            self.vm_writer.write_pop(segment_of_var, index_of_var)

        self.__process(SEMICOLON)
        self.is_method_invocation = True  # return to default

    def compile_if(self):
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

    def __get_next_label(self):
        label = "L" + str(self.label_index)
        self.label_index += 1
        return label

    def compile_while(self):
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

    def compile_do(self):
        self.__process('do')
        while self.tokenizer.current_token != ';':
            if self.tokenizer.current_token == '(':
                self.__process(self.tokenizer.current_token)
                self.compile_expression_list()
            if self.tokenizer.peek_next_token() == "(":
                # if it's a method invocation- add 'this' to args
                if self.invoked_class_name == self.class_name and self.is_method_invocation:
                    self.invoked_arg_count = 1
                    # Pushes the object on which the method is called to operate (implicit argument)
                    self.vm_writer.write_push(Segment.POINTER, 0)
                self.__process(self.tokenizer.current_token, scope=SUBROUTINE)
            elif self.tokenizer.peek_next_token() == ".":
                invoking_identifier = self.tokenizer.current_token
                identifier_category = self.symbol_table.kind_of(invoking_identifier)
                # if it's a call on an object= METHOD
                if identifier_category == IdentifierKind.VAR or identifier_category == IdentifierKind.FIELD \
                        or identifier_category == IdentifierKind.ARG:
                    self.invoked_class_name = self.symbol_table.type_of(invoking_identifier)
                    self.invoked_arg_count = 1  # add 'this' to args
                    self.is_method_invocation = True
                else:
                    self.invoked_class_name = invoking_identifier
                    self.is_method_invocation = False
                self.__process(self.tokenizer.current_token, scope=CLASS, is_used=True)

            else:
                self.__process(self.tokenizer.current_token)

        # the caller of a void method must dump the returned value
        self.vm_writer.write_pop(Segment.TEMP, 0)
        self.tokenizer.advance()
        self.is_method_invocation = True  # return to default

    def compile_return(self):
        self.__process(RETURN)
        # check if there's an expression
        if self.tokenizer.current_token != ';':
            self.compile_expression()
        else:
            # returns a value (all methods must return a value)
            self.vm_writer.write_push(Segment.CONST, 0)

        self.vm_writer.write_return()
        self.tokenizer.advance()

    def compile_expression(self):
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

    def compile_expression_list(self):
        num_of_expressions = 0
        while self.tokenizer.current_token != ')':
            if self.tokenizer.current_token == ',':
                self.__process(self.tokenizer.current_token)
            num_of_expressions += 1
            self.compile_expression()
        return num_of_expressions

    def compile_term(self):
        array_var_name = ''
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
                    invoking_identifier = self.tokenizer.current_token
                    identifier_category = self.symbol_table.kind_of(invoking_identifier)
                    # if it's a call on an object
                    if identifier_category == IdentifierKind.VAR or identifier_category == IdentifierKind.FIELD or \
                            identifier_category == IdentifierKind.ARG:
                        self.invoked_class_name = self.symbol_table.type_of(invoking_identifier)
                        self.invoked_arg_count = 1  # add 'this' to args
                        self.is_method_invocation = True
                    else:
                        self.invoked_class_name = invoking_identifier
                        self.is_method_invocation = False
                    self.__process(self.tokenizer.current_token, scope=CLASS, is_used=True)
                else:
                    if self.tokenizer.peek_next_token() == "[":
                        array_var_name = self.tokenizer.current_token
                        self.is_array_var = True
                    self.__process(self.tokenizer.current_token)
        while self.tokenizer.current_token in TERM_ENDING:
            if self.tokenizer.current_token == '[':  # Array term
                self.__process(self.tokenizer.current_token)
                self.compile_expression()

                segment_of_var, index_of_var = self.__get_segment_and_index_of_var(array_var_name)
                self.vm_writer.write_push(segment_of_var, index_of_var)
                self.vm_writer.write_line('add')

                self.vm_writer.write_pop(Segment.POINTER, 1)  # set pointer 1 to the entry’s address (arr + i)
                self.vm_writer.write_push(Segment.THAT, 0)  # access the entry by accessing that 0
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
            self.__process(self.tokenizer.current_token)
            self.in_unary = False

    def close(self):
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

        identifier_index = None
        if identifier_category != IdentifierKind.NONE:
            identifier_index = self.symbol_table.index_of(identifier_name)

        if is_used:
            if identifier_category_str == SUBROUTINE:  # used subroutine
                n_args = 0
                if self.invoked_arg_count == 1:  # METHOD call: meaning 'this' was added
                    n_args += self.invoked_arg_count
                self.tokenizer.advance()  # move after (
                self.tokenizer.advance()
                n_args += self.compile_expression_list()
                self.vm_writer.write_call(self.invoked_class_name + DOT + identifier_name, n_args)
                # set the default for a subroutine to be a METHOD
                self.invoked_class_name = self.class_name
                self.invoked_arg_count = 0

            elif (identifier_category == IdentifierKind.VAR or identifier_category == IdentifierKind.ARG
                  or identifier_category == IdentifierKind.FIELD or identifier_category == IdentifierKind.STATIC) \
                    and not self.is_array_var:
                segment_of_var = self.__get_var_segment_by_kind(identifier_category)
                self.vm_writer.write_push(segment_of_var, identifier_index)

            self.is_array_var = False

    def __get_segment_and_index_of_var(self, var_name):
        kind_of_var = self.symbol_table.kind_of(var_name)
        segment_of_var = self.__get_var_segment_by_kind(kind_of_var)
        index_of_var = self.symbol_table.index_of(var_name)
        return segment_of_var, index_of_var

    def __get_var_segment_by_kind(self, kind_of_var):
        if kind_of_var == IdentifierKind.STATIC:
            return Segment.STATIC
        elif kind_of_var == IdentifierKind.FIELD:
            return Segment.THIS
        elif kind_of_var == IdentifierKind.ARG:
            return Segment.ARG
        elif kind_of_var == IdentifierKind.VAR:
            return Segment.LOCAL
