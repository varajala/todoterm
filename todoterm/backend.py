import sqlite3 as sqlite
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


def with_connection(func: typing.Callable) -> typing.Callable:
    @functools.wraps(func)
    def wrapper(filepath: str, **kwargs) -> typing.Any:
        conn = create_connection(filepath)
        if conn is None:
            raise Error('Unbale to read data')
        
        try:
            return_value = func(conn, **kwargs)
            conn.commit()
            return return_value
        
        finally:
            conn.close()
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
    sql = "\n".join([
        'CREATE TABLE IF NOT EXISTS tasks (',
        '   id INTEGER PRIMARY KEY AUTOINCREMENT,',
        '   info TEXT NOT NULL,',
        '   done INTEGER DEFAULT 0',
        ');'
    ])
    conn.executescript(sql)


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
def do_tasks(conn: sqlite.Connection, task_ids: typing.List[int]):
    sql = 'UPDATE tasks SET done = 1 WHERE id = ?'
    try:
        conn.executemany(sql, map(lambda n: (n, ), task_ids))
    except sqlite.DatabaseError as err:
        raise SystemExit from err


@with_connection
@require_arguments('task_ids')
def undo_tasks(conn: sqlite.Connection, task_ids: typing.List[int]):
    sql = 'UPDATE tasks SET done = 0 WHERE id = ?'
    try:
        conn.executemany(sql, map(lambda n: (n, ), task_ids))
    except sqlite.DatabaseError as err:
        raise SystemExit from err


@with_connection
@require_arguments('task_ids')
def delete_tasks(conn: sqlite.Connection, task_ids: typing.List[int]):
    sql = 'DELETE FROM tasks WHERE id = ?'
    try:
        conn.executemany(sql, map(lambda n: (n, ), task_ids))
    except sqlite.DatabaseError as err:
        raise SystemExit from err
