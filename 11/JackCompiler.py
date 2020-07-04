import sys
import os.path
from os import path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
from VMWriter import VMWriter

USAGE_INSTRUCTION = 'Usage: JackAnalyzer <file.jack or directory>'
NO_VM_FILES = 'Error: No .jack files in directory'
FILE_OPEN_ERROR = 'Error: Cannot open file'
FILE_WRITE_ERROR = 'Error: Cannot write to file'
NO_FILES_ERROR = 'No .jack files found in the directory'
XML_EXTENSION = 'xml'
JACK_EXTENSION = 'jack'
DOT = '.'
BACK_SLASH = '\\'


def check_input_folder():
    folder_name = sys.argv[1]
    if folder_name[-1] == BACK_SLASH or folder_name[-1] == '"' or folder_name[-1] == "'":
        folder_name = folder_name[:-1]
    check_folder = path.isdir(folder_name)
    if check_folder:
        return folder_name
    return None


# Checking if arguments for program are ok and if file exists
def check_input():
    if len(sys.argv) is not 2:
        print(USAGE_INSTRUCTION)  # too many/less arguments
        sys.exit()
    file_split = sys.argv[1].strip().split(DOT)

    if len(file_split) < 2:
        return None

    ext = file_split[-1].strip().lower()

    if ext != JACK_EXTENSION:  # not .jack extension
        return None
    file_name = '.'.join(file_split[0:-1]).strip()
    check_file = path.exists(sys.argv[1])

    if check_file is False:  # file doesn't exists/can't open file
        print(FILE_OPEN_ERROR)
        sys.exit()
    if path.isdir(sys.argv[1]):
        return None
    elif path.isfile(sys.argv[1]):
        return file_name

    return None


# running the function to parse commands and write the translation to an .xml file
def parse_commands_and_write_output():
    if parser.has_more_tokens():
        parser.advance()
    code_writer.compile_class()


file_name = check_input()
if file_name is not None:  # this case handles single file
    parser = JackTokenizer(file_name + DOT + JACK_EXTENSION)
    try:
        code_writer = CompilationEngine(file_name, False, parser, SymbolTable(), VMWriter(file_name))
        parse_commands_and_write_output()
    except IOError:
        print(FILE_WRITE_ERROR)
        sys.exit()
else:
    path_name = check_input_folder()
    if path_name is None:
        print(USAGE_INSTRUCTION)
        sys.exit()
    try:  # this case handles a directory
        file_name = path_name.split(BACK_SLASH)[-1]
        files_to_parse = []
        for root, dirs, files in os.walk(path_name):
            for file_in_folder in files:
                check_extension = file_in_folder.split(DOT)[-1]
                if check_extension == JACK_EXTENSION:
                    files_to_parse.append(file_in_folder)
        number_of_files = len(files_to_parse)
        if number_of_files == 0:
            print(NO_FILES_ERROR)
            sys.exit()
        for jack_file in files_to_parse:
            parser = JackTokenizer(path_name + BACK_SLASH + jack_file)
            file_name = path_name + BACK_SLASH + jack_file.split(DOT)[0]
            code_writer = CompilationEngine(file_name, False, parser,
                                            SymbolTable(), VMWriter(file_name))
            parse_commands_and_write_output()
            code_writer.close()
    except IOError:
        print(FILE_WRITE_ERROR)
        sys.exit()
