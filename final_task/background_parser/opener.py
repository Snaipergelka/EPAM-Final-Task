import os

import textract


def get_content(filename):
    extension = os.path.splitext(filename)[-1]
    if extension in [".txt", ".py"]:
        return open(filename).read()
    else:
        return textract.process(filename).decode("utf-8")
