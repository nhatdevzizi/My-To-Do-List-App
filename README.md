# Task manager CLI

A small Python task manager with local JSON storage. Run it with:

```powershell
python main.py
```

The menu supports adding, viewing, listing, editing, deleting, completing,
reopening, filtering, and sorting tasks. A title is required; duration is a
non-negative number of minutes, and priority is an integer from 0 to 5.
Leave a field blank while editing to keep its current value. Enter `-` for
the description to clear it.

Data is stored in `data/tasks.json`. Successful changes save the entire task
collection. The file also stores the next ID, so deleting a task does not
reuse its ID. An existing empty file or older JSON list is accepted.

Run the tests with:

```powershell
python -m unittest discover -s tests -v
```
