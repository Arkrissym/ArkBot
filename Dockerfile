FROM debian:stretch AS build

RUN apt-get update && apt-get install -y \
	libssl-dev \
	autoconf \
	automake \
	build-essential \
	cmake \
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
	libxfixes3 \
	libxml2-dev

WORKDIR /ffmpeg
RUN wget -q -O ffmpeg-snapshot.tar.bz2 http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
RUN tar xjf ffmpeg-snapshot.tar.bz2

WORKDIR /ffmpeg/ffmpeg
RUN ./configure \
	--prefix="/usr" \
	--bindir="/usr/bin" \
	--enable-gpl \
	--enable-libmp3lame \
	--enable-libtheora \
	--enable-libvorbis \
	--enable-libvpx \
	--enable-libx264 \
	--enable-libx265 \
	--enable-nonfree \
	--enable-openssl \
	--enable-libxml2
RUN make -j4
RUN make install

FROM python:3.6-slim

WORKDIR /app

COPY --from=build /usr/bin/ffmpeg /usr/bin

COPY . /app

RUN apt-get update && apt-get install -y \
	libopus0 \
	libmp3lame0 \
	libtheora0 \
	libvorbis0a \
	libvpx4 \
	libx264-148 \
	libx265-dev \
	libssl-dev \
	libxcb1 \
	libxcb-shm0 \
	libxcb-xfixes0 \
	libxcb-shape0 \
	zlib1g \
	libasound2 \
	libsdl2-2.0-0 \
	libva1 \
	libva-drm1 \
	libvdpau1 \
	libxv1 \
	libxml2

RUN pip install -r requirements.txt
  
CMD ["python3", "bot.py"]
