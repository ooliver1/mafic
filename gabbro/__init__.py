# SPDX-License-Identifier: MIT
"""
Lavalink Client for Python
~~~~~~~~~~~~~~~~~~~~~~~~~~
A properly typehinted lavalink client for discord.py, nextcord, disnake and py-cord.
:copyright: (c) 2022-present ooliver1
:license: MIT, see LICENSE for more details.
"""

__title__ = "gabbro"
__author__ = "ooliver1"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present ooliver1"
__version__ = "0.1.0"

import logging

from . import libraries as __libraries

del __libraries

logging.getLogger(__name__).addHandler(logging.NullHandler())
