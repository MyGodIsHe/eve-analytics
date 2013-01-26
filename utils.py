import sys
import os


ROOT_DIR = os.path.normpath(
    os.path.abspath(os.path.dirname(__file__)))

def rel(*args):
    return os.path.join(ROOT_DIR, *args)

def print_progress(value):
    sys.stdout.write("\rProgress: %3d%%" % value)
    sys.stdout.flush()


def print_flush(text):
    sys.stdout.write("\r%s" % text)
    sys.stdout.flush()

def progress(items, count=None):
    progress = 0
    if count is None:
        count = len(items)

    print_progress(progress)

    for i, item in enumerate(items):
        yield item
        current_progress = 100 * (i + 1) / count
        if current_progress != progress:
            progress = current_progress
            print_progress(progress)
    print