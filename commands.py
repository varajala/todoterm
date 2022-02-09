from curses import keyname
import typing
import functools
import sys
import os
import argparse

import backend


class Colors:
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    CYAN    = '\033[96m'
    RESET   = '\033[0m'

CommandType = typing.Callable[[list, str], int]

commands: typing.Dict[str, CommandType] = dict()


def print_usage():
    pass


def print_error(message: str):
    sys.stdout.write(Colors.RED)
    sys.stdout.write('ERROR: ')
    sys.stdout.write(Colors.RESET)
    sys.stdout.write(message + '\n')


def require_data_file(func: CommandType) -> CommandType:
    @functools.wraps(func)
    def wrapper(args: typing.List[str], data_file: str) -> int:
        if not os.path.exists(data_file):
            print_error(f"No data file '{os.path.basename(data_file)}' in current directory.")
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


def register_command(alias: str) -> CommandType:
    def wrapper(func: CommandType) -> CommandType:
        commands[alias] = func
        return func
    return wrapper


@register_command('init')
def create_data_file(args: typing.List[str], data_file: str) -> int:
    try:
        backend.init_schema(data_file)
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0


@register_command('list')
@require_data_file
def list_tasks(args: typing.List[str], data_file: str) -> int:
    parser = argparse.ArgumentParser(prog='list', usage='%(prog)s [options]')
    parser.add_argument('-a', '--all',
        help='List all tasks. Default is only incompleted tasks.',
        action='store_true'
        )
    parser.add_argument('-d', '--done',
        action='store_true',
        help='List only completed tasks.'
    )
    options = parser.parse_args(args)
    
    tasks = None
    try:
        tasks = backend.retrieve_tasks(data_file)
    except backend.Error as error:
        print_error(str(error))
        return 1

    if options.all:
        tasks.sort(key = lambda t: int(t.done))
    
    elif options.done:
        tasks = list(filter(lambda t: t.done, tasks))
    
    else:
        tasks = list(filter(lambda t: not t.done, tasks))
    
    print(tasks)
    return 0


@register_command('add')
@require_data_file
def add_task(args: typing.List[str], data_file: str) -> int:
    if len(args) < 1:
        print_error('Description is required for the new task.')
        return 1
    
    task_info = args.pop(0)
    if not task_info:
        print_error("Task description can't be blank.")
        return 1
    
    try:
        backend.create_task(
            data_file,
            task = backend.Task(info = task_info)
            )
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0


@register_command('done')
@require_data_file
def do_task(args: typing.List[str], data_file: str) -> int:
    parser = argparse.ArgumentParser(prog='done', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        help='ID of the task.',
        )
    options = parser.parse_args(args)
    
    try:
        backend.do_tasks(
            data_file,
            task_ids = options.tasks
            )
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0


@register_command('undo')
@require_data_file
def do_task(args: typing.List[str], data_file: str) -> int:
    parser = argparse.ArgumentParser(prog='undo', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        help='ID of the task.',
        )
    options = parser.parse_args(args)
    
    try:
        backend.undo_tasks(
            data_file,
            task_ids = options.tasks
            )
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0


@register_command('del')
@require_data_file
def do_task(args: typing.List[str], data_file: str) -> int:
    parser = argparse.ArgumentParser(prog='del', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        help='ID of the task.',
        )
    options = parser.parse_args(args)
    
    try:
        backend.delete_tasks(
            data_file,
            task_ids = options.tasks
            )
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0
