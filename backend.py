import sqlite3 as sqlite
import os
import typing
import contextlib
import functools
from dataclasses import dataclass


class Error(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


@dataclass
class Task:
    info: str
    done: bool = False
    id: int = -1

    @staticmethod
    def from_dict(data: dict):
        task = Task(data.get('info', ''))
        task.id = data.get('id', -1)
        task.done = data.get('done', False)
        return task


connection: typing.Optional[sqlite.Connection] = None


def row_factory(cursor: sqlite.Cursor, row_data: typing.Tuple) -> Task:
    data = dict()
    for i, header in enumerate(cursor.description):
        data[header[0]] = row_data[i]
    return Task.from_dict(data)


def create_connection(filepath: str) -> typing.Optional[sqlite.Connection]:
    conn = None
    with contextlib.suppress(sqlite.DatabaseError, OSError):
        conn = sqlite.connect(filepath)
        conn.row_factory = row_factory
    return conn


def read_script(name: str) -> typing.Optional[str]:
    SQL_SCRIPT_DIR = 'sql'
    script_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        SQL_SCRIPT_DIR
        )

    script_path = os.path.join(script_folder, name)
    if not os.path.exists(script_path):
        return None

    with open(script_path, 'r') as file:
        return file.read()


def with_connection(func: typing.Callable) -> typing.Callable:
    @functools.wraps(func)
    def wrapper(filepath: str, **kwargs) -> typing.Any:
        global connection
        if connection is not None:
            return func(connection, **kwargs)
        
        conn = create_connection(filepath)
        if conn is None:
            raise Error('Unbale to read data')
        connection = conn
        
        try:
            return_value = func(conn, **kwargs)
            conn.commit()
            return return_value
        
        finally:
            conn.close()
            connection = None
    return wrapper


def require_arguments(*args):
    def outer_wrapper(func):
        def inner_wrapper(data_file: str, **kwargs):
            arguments = list()
            for argument in args:
                if argument not in kwargs:
                    raise SystemExit(f"Function '{func.__qualname__}' missing argument '{argument}'")
                arguments.append(kwargs.pop(argument))
            return func(data_file, *tuple(arguments), **kwargs)
        return inner_wrapper
    return outer_wrapper


@with_connection
def init_schema(conn: sqlite.Connection, *args):
    SCRIPT_FILE = 'schema.sql'
    script = read_script(SCRIPT_FILE)
    if script is None:
        raise SystemExit(f"FATAL ERROR - Script not found: '{SCRIPT_FILE}'")
    conn.executescript(script)


@with_connection
def retrieve_tasks(conn: sqlite.Connection, *args):
    cursor = conn.execute("SELECT * FROM tasks")
    return cursor.fetchall()


@with_connection
@require_arguments('task')
def create_task(conn: sqlite.Connection, task: Task):
    sql = 'INSERT INTO tasks (info, done) VALUES (?, ?)'
    try:
        conn.execute(sql, (task.info, task.done))
    except sqlite.DatabaseError as err:
        raise SystemExit from err


@with_connection
@require_arguments('task_ids')
def do_tasks(conn: sqlite.Connection, task_ids: typing.List[str]):
    sql = 'UPDATE tasks SET done = 1 WHERE id = ?'
    try:
        conn.executemany(sql, task_ids)
    except sqlite.DatabaseError as err:
        raise SystemExit from err


@with_connection
@require_arguments('task_ids')
def undo_tasks(conn: sqlite.Connection, task_ids: typing.List[str]):
    sql = 'UPDATE tasks SET done = 0 WHERE id = ?'
    try:
        conn.executemany(sql, task_ids)
    except sqlite.DatabaseError as err:
        raise SystemExit from err


@with_connection
@require_arguments('task_ids')
def delete_tasks(conn: sqlite.Connection, task_ids: typing.List[str]):
    sql = 'DELETE FROM tasks WHERE id = ?'
    try:
        conn.executemany(sql, task_ids)
    except sqlite.DatabaseError as err:
        raise SystemExit from err
