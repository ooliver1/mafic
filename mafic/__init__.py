# SPDX-License-Identifier: MIT
"""
Mafic
=====
A properly typehinted lavalink client for discord.py, nextcord, disnake and py-cord.

:copyright: (c) 2022-present ooliver1
:license: MIT, see LICENSE for more details.
"""

import logging

from . import __libraries
from .errors import *
from .events import *
from .filter import *
from .ip import *
from .node import *
from .player import *
from .playlist import *
from .pool import *
from .region import *
from .search_type import *
from .stats import *
from .strategy import *
from .track import *
from .warnings import *

__title__ = "mafic"
__author__ = "ooliver1"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present ooliver1"
__version__ = "2.0.0"
"""The current version of mafic, using `PEP 440`_ format.

.. _PEP 440: https://peps.python.org/pep-0440/
"""

del __libraries

logging.getLogger(__name__).addHandler(logging.NullHandler())
