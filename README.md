# todoterm

A simple TODO command line application.


## Installation

    python -m pip install todoterm


## Usage

First create a sqlite database file with the following command:

    python -m todoterm init


This creates a sqlite database file named **.todo** in the current working directory.
Todoterm always modifies the database in the current working directory.


Next add new tasks with the following command:

    python -m todoterm add "Task description here..."


List tasks with the **list** - command:

    python -m todoterm list


Delete tasks with the **del** - command:

    python -m todoterm del 1


Mark tasks as done with the **done** - command:

    python -m todoterm done 1


Undo tasks with the **undo** - command:

    python -m todoterm done 1


The del, done and undo commands require atleast one integer value as input.
These integers are the IDs of the modified tasks. You can see them in the output of the
list command. To get all available options for each command, use option **--help**.