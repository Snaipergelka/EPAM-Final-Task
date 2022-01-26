import os


def get_walker(path, file_extensions):
    return (
        (p, folders, [file for file in files if os.path.splitext(file)[-1] in file_extensions])
        for p, folders, files in os.walk(path, topdown=False))
