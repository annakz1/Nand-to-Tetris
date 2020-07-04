from enum import Enum

DOT = '.'
VM_EXTENSION = 'vm'
POP = "pop"
PUSH = "push"


class Segment(Enum):
    CONST = 1
    ARG = 2
    LOCAL = 3
    STATIC = 4
    THIS = 5
    THAT = 6
    POINTER = 7
    TEMP = 8

class Command(Enum):
    ADD = 1
    SUB = 2
    NEG = 3
    EQ = 4
    GT = 5
    LT = 6
    AND = 7
    OR = 8
    NOT = 9

class VMWriter:

    def __init__(self, file_name):
        """
        creates a new output.vm file and prepares it for writing
        """
        self.output_file = open(file_name + DOT + VM_EXTENSION, "w")

    def write_push(self, segment: Segment, index):
        """
        writes a VM push command
        """
        segment_str = segment.name.lower()
        if segment == Segment.CONST:
            segment_str = 'constant'
        self.write_line(PUSH + " " + segment_str + " " + str(index))

    def write_pop(self, segment: Segment, index):
        """
        writes a VM pop command
        """
        segment_str = segment.name.lower()
        if segment == Segment.CONST:
            segment_str = 'constant'
        self.write_line(POP + " " + segment_str + " " + str(index))

    def write_arithmetic(self, command: Command):
        """
        writes a VM arithmetic-logical command
        """
        self.write_line(command.name.lower())

    def write_label(self, label):
        """
        writes a VM label command
        """
        self.write_line("label " + label)

    def write_goto(self, label):
        """
        writes a VM goto command
        """
        self.write_line("goto " + label)

    def write_if(self, label):
        """
        writes a VM if-goto command
        """
        self.write_line("if-goto " + label)

    def write_call(self, name, n_args):
        """
        writes a VM call command
        """
        self.write_line("call " + name + " " + str(n_args))

    def write_function(self, name, n_locals):
        """
        writes a VM function command
        """
        self.write_line("function " + name + " " + str(n_locals))

    def write_return(self):
        """
        writes a VM return command
        """
        self.write_line("return")

    def write_line(self, line):
        self.output_file.write(line + '\n')

    def close(self):
        self.output_file.close()
