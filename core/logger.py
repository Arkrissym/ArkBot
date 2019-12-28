# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import logging

parent_logger = logging.getLogger('discord')
parent_logger.setLevel(logging.DEBUG)

logger = parent_logger.getChild("application")

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))

parent_logger.addHandler(ch)
