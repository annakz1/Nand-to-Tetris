from Parser import CommandType

ASM_EXTENSION = 'asm'
DOT = '.'
BACK_SLASH = '\\'
ADD = 'add'
SUBSTRACT = 'sub'
NEG = 'neg'
EQUALIZER = 'eq'
GREATERTHAN = 'gt'
LOWERTHAN = 'lt'
AND = 'and'
OR = 'or'
NOT = 'not'

SEGMENT_ARGUMENT = 'argument'
SEGMENT_LOCAL = 'local'
SEGMENT_STATIC = 'static'
SEGMENT_CONSTANT = 'constant'
SEGMENT_THIS = 'this'
SEGMENT_THAT = 'that'
SEGMENT_POINTER = 'pointer'
SEGMENT_TEMP = 'temp'

LOCAL_ADDRESS = 'LCL'
ARGUMENT_ADDRESS = 'ARG'
STATIC_ADDRESS = 16
THIS_ADDRESS = 'THIS'
THAT_ADDRESS = 'THAT'
TEMP_ADDRESS = 5
POINTER_ADDRESS = 3

COMPARISION_LOOP_SYMBOL = 'COMPARISION_LOOP_'
END_COMPARISION_LOOP_SYMBOL = 'END_COMPARISION_LOOP_'
RETURN_LABEL_SYMBOL = '$ret.'

SEGMENT_DICTIONARY = {'local': LOCAL_ADDRESS, 'argument': ARGUMENT_ADDRESS,
                      'this': THIS_ADDRESS, 'that': THAT_ADDRESS,
                      'temp': TEMP_ADDRESS, 'static': STATIC_ADDRESS, 'pointer': POINTER_ADDRESS}


class CodeWriter:
    def __init__(self, file_name):
        self.output_file = open(file_name + DOT + ASM_EXTENSION, "w")
        self.file_name = file_name.split(BACK_SLASH)[-1]
        self.comparisons_counter = 0
        self.return_label_counter = 0
        self.__initialize_program()

    def __initialize_program(self):
        self.__write_line('@256')
        self.__write_line('D=A')
        self.__write_line('@SP')
        self.__write_line('M=D')
        self.write_call('Sys.init', 0)

    def __write_line(self, line):
        self.output_file.write(line + '\n')

    def __deal_with_arithmetic(self, command):
        if command == ADD:
            self.__write_line('M=D+M')
        elif command == SUBSTRACT:
            self.__write_line('M=M-D')
        elif command == NEG:
            self.__write_line('M=-M')
        elif command in [EQUALIZER, GREATERTHAN, LOWERTHAN]:
            self.comparisons_counter += 1
            self.__write_line('D=M-D')
            self.__write_line('@' + COMPARISION_LOOP_SYMBOL + str(self.comparisons_counter))
            if command == EQUALIZER:
                self.__write_line('D;JEQ')
            elif command == GREATERTHAN:
                self.__write_line('D;JGT')
            else:
                self.__write_line('D;JLT')
            self.__handle_comparision_jumps()
        elif command == AND:
            self.__write_line('M=M&D')
        elif command == OR:
            self.__write_line('M=M|D')
        else:
            self.__write_line('M=!M')

    def write_label(self, label):
        self.__write_line('({})'.format(label))

    def write_goto(self, label):
        self.__write_line('@' + label)
        self.__write_line('0;JMP')

    def write_if(self, label):
        self.__put_stack_top_into_A()
        self.__write_line('D=M')
        self.__write_line('@' + label)
        self.__write_line('D;JNE')

    def write_function(self, function_name, n_vars):
        self.write_label(function_name)
        self.__write_line('@LCL')
        self.__write_line('A=M')
        # Initialize the local variables of the callee
        for var in range(n_vars):
            self.__write_line('M=0')
            self.__write_line('A=A+1')
            self._from_stack_to_memory_transporter('LCL', str(var))

    def write_call(self, function_name, n_args):
        self.__write_line('@' + function_name + RETURN_LABEL_SYMBOL + str(self.return_label_counter))
        self.__write_line('D=A')
        self.__put_D_into_stack_top()  # Store return address (caller) in stack
        self.__increment_SP()
        self.__push_value_for_segment_pointer(LOCAL_ADDRESS)
        self.__push_value_for_segment_pointer(ARGUMENT_ADDRESS)
        self.__push_value_for_segment_pointer(THIS_ADDRESS)
        self.__push_value_for_segment_pointer(THAT_ADDRESS)
        self.__put_index_in_D(n_args + 5)
        self.__write_line('@SP')
        self.__write_line('D=M-D')
        self.__write_line('@' + ARGUMENT_ADDRESS)
        self.__write_line('M=D')
        self.__write_line('@SP')
        self.__write_line('D=M')
        self.__write_line('@' + LOCAL_ADDRESS)
        self.__write_line('M=D')
        self.write_goto(function_name)
        self.write_label(function_name + RETURN_LABEL_SYMBOL + str(self.return_label_counter))
        self.return_label_counter += 1

    def __push_value_for_segment_pointer(self, segment_symbol):
        self.__write_line('@' + segment_symbol)
        self.__write_line('D=M')
        self.__put_D_into_stack_top()
        self.__increment_SP()

    def restore_value_for_segment_pointer(self, segment_symbol, distance_from_lcl):
        self.__write_line('@' + distance_from_lcl)
        self.__write_line('D=A')
        self.__write_line('@R14')
        self.__write_line('A=M-D')
        self.__write_line('D=M')
        self.__write_line('@' + segment_symbol)
        self.__write_line('M=D')

    def __save_LCL_to_R14(self):
        # save original LCL
        self.__write_line('@LCL')
        self.__write_line('D=M')
        self.__write_line('@R14')
        self.__write_line('M=D')

    def __save_ret_address_to_R15(self):
        self.__write_line('@5')
        self.__write_line('D=A')
        self.__write_line('@R14')
        self.__write_line('D=M-D')
        self.__write_line('A=D')
        self.__write_line('D=M')
        self.__write_line('@R15')
        self.__write_line('M=D')

    def __set_ARG_to_D(self):
        self.__write_line('@ARG')
        self.__write_line('A=M')
        self.__write_line('M=D')

    def __set_SP_to_ARG_plus_one(self):
        self.__write_line('@ARG')
        self.__write_line('D=M+1')
        self.__write_line('@SP')
        self.__write_line('M=D')

    def __jump_to_return_address(self):
        self.__write_line('@R15')
        self.__write_line('A=M')
        self.__write_line('0;JMP')

    def write_return(self):
        self.__save_LCL_to_R14()
        self.__save_ret_address_to_R15()
        self.__put_stack_top_to_D()
        self.__set_ARG_to_D()
        self.__set_SP_to_ARG_plus_one()
        self.restore_value_for_segment_pointer(THAT_ADDRESS, '1')
        self.restore_value_for_segment_pointer(THIS_ADDRESS, '2')
        self.restore_value_for_segment_pointer(ARGUMENT_ADDRESS, '3')
        self.restore_value_for_segment_pointer(LOCAL_ADDRESS, '4')
        self.__jump_to_return_address()

    def set_file_name(self, fileName):
        self.file_name = fileName.split(BACK_SLASH)[-1]

    def write_arithmetic(self, command):
        if command not in [NEG, NOT]:
            self.__put_stack_top_to_D()
        self.__put_stack_top_into_A()
        self.__deal_with_arithmetic(command)
        self.__increment_SP()

    # sets the address for the segment and the index for temp,pointer,static and constant cases
    def __set_address_for_segment(self, segment, index):
        if segment in [SEGMENT_TEMP, SEGMENT_POINTER]:
            address = '@R' + str(SEGMENT_DICTIONARY[segment] + index)
        elif segment == SEGMENT_STATIC:
            address = '@' + self.file_name + DOT + str(index)
        elif segment != SEGMENT_CONSTANT:
            address = '@' + SEGMENT_DICTIONARY[segment]
        else:
            address = ''
        return address

    def write_push_pop(self, command, segment, index):
        address = self.__set_address_for_segment(segment, index)
        if command == CommandType.C_POP:
            if segment in [SEGMENT_TEMP, SEGMENT_POINTER, SEGMENT_STATIC]:
                self.__put_stack_top_to_D()
                self.__write_line(address)
                self.__write_line('M=D')
            else:
                self.__put_index_in_D(index)
                self.__save_address_with_index_into_temp(address)
                self.__put_stack_top_to_D()
                self.__put_D_in_address_of_temp()
        elif command == CommandType.C_PUSH:
            if segment in [SEGMENT_TEMP, SEGMENT_POINTER, SEGMENT_STATIC]:
                self.__write_line(address)
                self.__write_line('D=M')
            else:
                self.__put_index_in_D(index)
                if segment != SEGMENT_CONSTANT:
                    self.__write_line(address)
                    self.__write_line('A=M+D')
                    self.__write_line('D=M')
            self.__put_D_into_stack_top()
            self.__increment_SP()

    """ handling comparision situation where a new symbol need to be used to distinguish between
        the situation where the comparision return true and false, we do that by creating labels
        jumping between them """

    def __handle_comparision_jumps(self):
        self.__write_line('@SP')
        self.__write_line('A=M')
        self.__write_line('M=0')
        self.__write_line('@' + END_COMPARISION_LOOP_SYMBOL + str(self.comparisons_counter))
        self.__write_line('0;JMP')
        self.__write_line('(' + COMPARISION_LOOP_SYMBOL + str(self.comparisons_counter) + ')')
        self.__write_line('@SP')
        self.__write_line('A=M')
        self.__write_line('M=-1')
        self.__write_line('(' + END_COMPARISION_LOOP_SYMBOL + str(self.comparisons_counter) + ')')

    def __increment_SP(self):
        self.__write_line('@SP')
        self.__write_line('M=M+1')

    def __decrement_SP(self):
        self.__write_line('@SP')
        self.__write_line('M=M-1')

    def __put_index_in_D(self, index):
        self.__write_line('@' + str(index))
        self.__write_line('D=A')

    def __put_D_into_stack_top(self):
        self.__write_line('@SP')
        self.__write_line('A=M')
        self.__write_line('M=D')

    # dealing with a situation where we need to use a temp memory address in order to do operation on 2 variables
    def __save_address_with_index_into_temp(self, address):
        self.__write_line(address)
        self.__write_line('D=M+D')
        self.__write_line('@R13')
        self.__write_line('M=D')

    # taking the data out of temp memory address used before in order to complete the operation on 2 variables
    def __put_D_in_address_of_temp(self):
        self.__write_line('@R13')
        self.__write_line('A=M')
        self.__write_line('M=D')

    def __put_stack_top_to_D(self):
        self.__put_stack_top_into_A()
        self.__write_line('D=M')

    def __put_stack_top_into_A(self):
        self.__decrement_SP()
        self.__write_line('A=M')

    def close(self):
        self.output_file.close()

    def _from_stack_to_memory_transporter(self, segment, index):
        # return ('// pop from stack to segment {} {} \n'.format(segment, index) +
        self.__write_line('@{}'.format(index))
        self.__write_line('D=A')
        self.__write_line('@{}'.format(segment))
        self.__write_line('D=D+M')
        self.__write_line('@R13')
        self.__write_line('M=D')  # Store memory index where we want to store in R13
        self.load_stack_head_to_D()
        self.__write_line('@R13')
        self.__write_line('A=M')
        self.__write_line('M=D')

    def load_stack_head_to_D(self):
        self.__write_line('@SP')
        self.__write_line('AM=M-1')
        self.__write_line('D=M')
        self.__write_line('M=0')
