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
    def wrapper(filepath: str) -> typing.Any:
        global connection
        if connection is not None:
            return func(connection)
        
        conn = create_connection(filepath)
        if conn is None:
            raise Error('Unbale to read data')
        connection = conn
        
        try:
            return_value = func(conn)
            conn.commit()
            return return_value
        
        finally:
            conn.close()
            connection = None
    return wrapper


@with_connection
def init_schema(conn: sqlite.Connection):
    script = read_script('schema.sql')
    if script is None:
        raise SystemExit("FATAL ERROR - Script not found: 'schema.sql'")
    conn.executescript(script)
