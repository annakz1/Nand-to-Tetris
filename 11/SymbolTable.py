from enum import Enum


class IdentifierKind(Enum):
    STATIC = 1
    FIELD = 2
    ARG = 3
    VAR = 4
    NONE = 5


class SymbolTable:

    def __init__(self):
        self.class_level_table = dict()
        self.class_level_static_index = 0
        self.class_level_field_index = 0
        self.subroutine_level_table = dict()
        self.subroutine_level_argument_index = 0
        self.subroutine_level_local_index = 0

    def start_subroutine(self):
        """
        starts a new subroutine scope- resets the subroutine table
        """
        self.subroutine_level_table = dict()
        self.subroutine_level_argument_index = 0
        self.subroutine_level_local_index = 0

    def define(self, name, type, kind: IdentifierKind):
        """
        defines a new identifier and assigns it a running index

        :param name: identifier's name
        :param type: identifier's type
        :param kind: identifier's kind: STATIC, FIELD, ARG or VAR
        """
        if kind == IdentifierKind.STATIC:
            self.class_level_static_index += 1
            self.class_level_table[name] = [type, kind, self.class_level_static_index]
        elif kind == IdentifierKind.FIELD:
            self.class_level_field_index += 1
            self.class_level_table[name] = [type, kind, self.class_level_field_index]
        elif kind == IdentifierKind.ARG:
            self.subroutine_level_argument_index += 1
            self.subroutine_level_table[name] = [type, kind, self.subroutine_level_argument_index]
        else:
            self.subroutine_level_local_index += 1
            self.subroutine_level_table[name] = [type, kind, self.subroutine_level_local_index]

    def var_count(self, kind: IdentifierKind):
        """
        returns the number of variables of the given kind already defined in the current scope

        :param kind: identifier's kind: STATIC, FIELD, ARG or VAR
        :return: number of variables
        """
        if kind == IdentifierKind.STATIC:
            return self.class_level_static_index
        elif kind == IdentifierKind.FIELD:
            return self.class_level_field_index
        elif kind == IdentifierKind.ARG:
            return self.subroutine_level_argument_index
        else:
            return self.subroutine_level_local_index

    def kind_of(self, name) -> IdentifierKind:
        """
        returns the kind of the named identifier in the current scope.
        if the identifier is unknown in the current scope, returns NONE

        :param name: identifier's name
        :return: STATIC, FIELD, ARG, VAR, NONE
        """
        if name in self.class_level_table:
            return self.class_level_table[name][1]
        elif name in self.subroutine_level_table:
            return self.subroutine_level_table[name][1]
        else:
            return IdentifierKind.NONE

    def type_of(self, name):
        """
        returns the type of the named identifier in the current scope.

        :param name: identifier's name
        :return: identifier's type
        """
        if name in self.class_level_table:
            return self.class_level_table[name][0]
        elif name in self.subroutine_level_table:
            return self.subroutine_level_table[name][0]

    def index_of(self, name):
        """
        returns the index assignedto  the named identifier

        :param name: identifier's name
        :return: identifier's index
        """
        if name in self.class_level_table:
            return self.class_level_table[name][2]
        elif name in self.subroutine_level_table:
            return self.subroutine_level_table[name][2]
