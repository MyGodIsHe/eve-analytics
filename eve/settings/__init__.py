from django import *
from eve import *

try:
    from local import *
except ImportError:
    pass