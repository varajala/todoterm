import sys
import os
import typing

import commands


def main(argv: typing.List[str]) -> int:
    data_file =  os.path.join(os.getcwd(), '.todo')
    if not os.path.exists(data_file):
        return 1

    return commands.run(argv, data_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
