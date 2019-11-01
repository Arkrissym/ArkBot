# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))

logger.addHandler(ch)
