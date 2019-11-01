#!/bin/bash

# MIT License
# see LICENSE for details

# Copyright (c) 2017-2018 Arkrissym

apt-get update
apt-get install python3 libopus0
#apt-get install ffmpeg

python3 -m pip install -U -r requirements.txt

#ffmpeg from source
apt-get install libssl-dev \
	autoconf \
	automake \
	build-essential \
	cmake \
	libass-dev \
	libsdl2-dev \
	libtheora-dev \
	libtool \
	libva-dev \
	libvdpau-dev \
	libvorbis-dev \
	libxcb1-dev \
	libxcb-shm0-dev \
	libxcb-xfixes0-dev \
	mercurial \
	pkg-config \
	texinfo \
	wget \
	zlib1g-dev \
	libmp3lame-dev \
	libvpx-dev \
	libx265-dev \
	libx264-dev \
	yasm \
	libgl1-mesa-glx \
	libxdamage1 \
	libxfixes3

wget -q -O ffmpeg-snapshot.tar.bz2 http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjf ffmpeg-snapshot.tar.bz2
cd ffmpeg

./configure \
	--prefix="/usr" \
	--bindir="/usr/bin" \
	--enable-gpl \
	--enable-libass \
	--enable-libmp3lame \
	--enable-libtheora \
	--enable-libvorbis \
	--enable-libvpx \
	--enable-libx264 \
	--enable-libx265 \
	--enable-nonfree \
	--enable-openssl

make -j4
make install
