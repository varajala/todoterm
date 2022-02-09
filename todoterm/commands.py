import typing
import functools
import sys
import os
import argparse

import todoterm.backend as backend


class Colors:
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    RESET   = '\033[0m'

CommandType = typing.Callable[[list, str], int]

commands: typing.Dict[str, CommandType] = dict()


def print_tasks(tasks: typing.List[backend.Task]):
    if not tasks:
        sys.stdout.write('Empty...\n')
        return
    
    max_id = max(map(lambda t: t.id, tasks))

    for task in tasks:
        sys.stdout.write(str(task.id).zfill(len(str(max_id))))
        sys.stdout.write(f" {Colors.GREEN}[ x ]{Colors.RESET} - " if task.done else f" [   ] - ")
        sys.stdout.write(task.info)
        sys.stdout.write('\n')
    
    sys.stdout.write('\n')
    sys.stdout.write(Colors.GREEN)
    sys.stdout.write(str(len(tasks)))
    sys.stdout.write(Colors.RESET)
    sys.stdout.write(" results.\n")



def print_usage():
    sys.stdout.write('usage: [command]\n\n')
    sys.stdout.write('commands:\n')
    
    for name, command in commands.items():
        sys.stdout.write('  ' + name.ljust(6))
        sys.stdout.write(command.__doc__)
        sys.stdout.write('\n')


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
    if not sys.stdout.isatty() or sys.platform.startswith('win'):
        Colors.GREEN = Colors.RED = Colors.RESET = ''
    
    if not args:
        print_usage()
        return 1

    command_name = args.pop(0)
    command = commands.get(command_name, None)
    if command is None:
        print_error(
            f"Unknown command: '{command_name}'."
            +  " See 'help' for all available commands."
        )
        return 1
    
    return command(args, data_file)


def register_command(alias: str) -> CommandType:
    def wrapper(func: CommandType) -> CommandType:
        commands[alias] = func
        return func
    return wrapper


@register_command('help')
def show_help(args: typing.List[str], data_file: str) -> int:
    """Show this help message and exit."""
    print_usage()
    return 0


@register_command('init')
def create_data_file(args: typing.List[str], data_file: str) -> int:
    """Creates a data file into the current working directory."""
    parser = argparse.ArgumentParser(prog='init', usage='%(prog)s [options]')
    parser.parse_args(args)
    
    try:
        backend.init_schema(data_file)
    except backend.Error as error:
        print_error(str(error))
        return 1
    return 0


@register_command('list')
@require_data_file
def list_tasks(args: typing.List[str], data_file: str) -> int:
    """List saved tasks."""
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
    
    print_tasks(tasks)
    return 0


@register_command('add')
@require_data_file
def add_task(args: typing.List[str], data_file: str) -> int:
    """Create new task with the given description."""
    parser = argparse.ArgumentParser(prog='add', usage='%(prog)s [options]')
    parser.add_argument('description',
        help='Description for the new task',
        )
    options = parser.parse_args(args)
    
    task_info = options.description
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
    """Mark tasks as done. Takes a listing of task IDs as argument."""
    parser = argparse.ArgumentParser(prog='done', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        type=int,
        help='IDs of the updated tasks.',
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
def undo_task(args: typing.List[str], data_file: str) -> int:
    """Undo tasks. Takes a listing of task IDs as argument."""
    parser = argparse.ArgumentParser(prog='undo', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        type=int,
        help='IDs of the updated tasks.',
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
def delete_task(args: typing.List[str], data_file: str) -> int:
    """Delete tasks. Takes a listing of task IDs as argument."""
    parser = argparse.ArgumentParser(prog='del', usage='%(prog)s [options]')
    parser.add_argument('tasks',
        nargs='+',
        type=int,
        help='IDs of the deleted tasks.',
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
