import typing
import functools
import sys
import os


class Colors:
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    CYAN    = '\033[96m'
    RESET   = '\033[0m'


commands: typing.Dict[str, typing.Callable[[list, str], int]] = dict()


def print_usage():
    pass


def print_error(message: str):
    sys.stdout.write(Colors.RED)
    sys.stdout.write('ERROR: ')
    sys.stdout.write(Colors.RESET)
    sys.stdout.write(message + '\n')


def require_data_file(func: typing.Callable) -> typing.Callable:
    @functools.wraps(func)
    def wrapper(args: typing.List[str], data_file: str) -> int:
        if not os.path.exists(data_file):
            commands.print_error(f"No data file '{os.path.basename(data_file)}' in current directory.")
            return 1
        return func(args, data_file)
    return wrapper


def run(args: typing.List[str], data_file: str) -> int:
    if not args:
        print_usage()
        return 1

    command_name = args.pop(0)
    command = commands.get(command_name, None)
    if command is None:
        print_error(f"Unknown command: '{command_name}'.")
        return 1
    
    return command(args, data_file)


def add_command(alias: str):
    def wrapper(func: typing.Callable) -> int:
        commands[alias] = func
        return func()
    return wrapper
