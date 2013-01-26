from django import *
from logging import *
from eve import *

try:
    from local import *
except ImportError:
    pass