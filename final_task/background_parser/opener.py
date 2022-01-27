import os

import textract


def get_content(filename: str):
    """
    Chooses which open function to use on the criteria of extension.
    :param str filename: name of the file to open.
    """
    extension = os.path.splitext(filename)[-1]
    if extension in [".txt", ".py"]:
        return open(filename).read()
    else:
        try:
            return textract.process(filename).decode("utf-8")
        except Exception :
            return ""
