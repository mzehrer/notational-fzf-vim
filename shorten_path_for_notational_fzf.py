#!/usr/bin/env pypy3
# encoding: utf-8

import os
import sys
from pathlib import PurePath


def expand_path(path: str) -> str:
    ''' Expand tilde and return absolute path. '''

    return os.path.abspath(os.path.expanduser(path))


# These are floated to the top so they aren't recalculated every loop
REPLACEMENTS = ('', os.pardir, '~')
old_paths = [expand_path(replacement) for replacement in REPLACEMENTS]


def prettyprint_path(path: str, old_path: str, replacement: str) -> str:
    # Pretty print the path prefix
    path = path.replace(old_path, replacement, 1)
    # Truncate the rest of the path to a single character.
    short_path = os.path.join(replacement, * [x[0] for x in PurePath(path).parts[1:]])
    return short_path


def shorten(path: str) -> str:
    # We don't want to shorten the filename, just its parent directory, so we
    # `split()` and just shorten `path`.
    path, filename = os.path.split(path)

    # use empty replacement for current directory. it expands correctly

    for replacement, old_path in zip(REPLACEMENTS, old_paths):
        if path.startswith(old_path):
            short_path = prettyprint_path(path, old_path, replacement)
            # to avoid multiple replacements
            break

    # If no replacement was found, shorten the entire path.
    else:
        short_path = os.path.join(* [x[0] for x in PurePath(path).parts])

    return os.path.join(short_path, filename)


def process_line(line: str) -> None:
    # Expected format is colon separated `name:linenum:contents`
    filename, linenum, contents = line.split(sep=':', maxsplit=2)

    # Normalize path for further processing.
    filename = expand_path(filename)

    # Drop trailing newline.
    contents = contents.rstrip()

    # Format is: long form, short form, rest of line. This is so Vim can process it.
    formatted_line = ':'.join([filename, linenum] + [shorten(filename), linenum] + [contents])

    # We print the long and short forms, and one form is picked in the Vim script that uses this.
    print(formatted_line)


if __name__ == '__main__':
    for line in sys.stdin:
        process_line(line)

