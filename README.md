# todoterm

A simple TODO command line application.


## Installation

    python -m pip install todoterm


## Usage

First create a sqlite database file with the following command:

    python -m todoterm init


This creates a file named **.todo** in the current working directory.
Next add new tasks with the following command:

    python -m todoterm add "Task description here..."


List tasks with the **list** - command:

    python -m todoterm list


List tasks with the **del** - command:

    python -m todoterm del


Mark tasks as done with the **done** - command:

    python -m todoterm done 1


Undo tasks with the **undo** - command:

    python -m todoterm done 1


To get all available options for each command, use option **--help**.