import sys
import os
import typing

import todoterm.commands as commands


def main(argv: typing.List[str]) -> int:
    DATA_FILE_NAME = '.todo'
    data_file =  os.path.join(os.getcwd(), DATA_FILE_NAME)
    return commands.run(argv, data_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
