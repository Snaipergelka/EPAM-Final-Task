import os
from typing import Iterator


def get_walker(path: str, file_extensions: list[str]) -> Iterator:
    """
    Returns generator of paths of files and folder from top folder.
    :return: paths of files and folders.
    :rtype: iterator
    """
    return (
        (
            p,
            folders,
            [
                file for file in files if
                os.path.splitext(file)[-1]
                in file_extensions
            ]
         )
        for p, folders, files in os.walk(path, topdown=False))
