#!/bin/bash

apt-get update
apt-get install python3 mbuffer
#apt-get install ffmpeg

python3 -m pip install -U -r requirements.txt
