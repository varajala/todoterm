import typing


commands: typing.Dict[str, typing.Callable] = dict()


def run(args: typing.List[str], data_file: str) -> int:
    return 0


def add_command(alias: str):
    def wrapper(func: typing.Callable) -> int:
        commands[alias] = func
        return func()
    return wrapper
