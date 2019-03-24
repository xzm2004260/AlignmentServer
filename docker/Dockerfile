#
# numpy, scipy, pdnn, and htk
# @author Georgi Dzhambazov
# v1.0.0
#
#
FROM ubuntu:16.04

MAINTAINER Georgi Dzhambazov <info@voicemagix.com>

# working directory
ENV HOME /Users/joro/Downloads/
ENV LANG C.UTF-8
WORKDIR $HOME


# packages list
RUN apt-get update
RUN apt-get install -y \
    libx11-dev \
    gawk \
    python-dev \
    python-pip \
    curl \
    git psmisc

RUN ln -s /usr/bin/python3 python

# pip
RUN pip install --upgrade pip

# copy & install compat-gcc-34-c++ compat-gcc-34
#COPY lib/*.deb $HOME/
#RUN \
#    dpkg -i $HOME/compat-gcc-34-c++_3.4.6-20_amd64.deb && \
#    dpkg -i $HOME/compat-gcc-34-c++_3.4.6-20_amd64.deb


# essentia dependencies
RUN apt-get install -y libyaml-0-2 libfftw3-3 libtag1v5 libsamplerate0 \ 
libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 \
libavresample-ffmpeg2 python python-numpy libpython2.7 python-numpy python-yaml python-six

# git and its dependencies
RUN apt-get install -y build-essential libyaml-dev libfftw3-dev \
libavcodec-dev libavformat-dev libavutil-dev libavresample-dev \
python-dev libsamplerate0-dev libtag1-dev python-numpy-dev git

# install essentia
RUN git clone -b pabloEntropia-viterbi-forced https://github.com/georgid/essentia
WORKDIR $HOME/essentia
RUN python ./waf configure --with-python --include-algos=MelBands,TriangularBands,DCT,MFCC,FrameCutter,Viterbi,FileOutputProxy --arch=x64 --pythondir=/usr/local/lib/python3.5/dist-packages/
RUN python ./waf install


# Alignment dependencies
#RUN git clone https://georgid:7Navuhodonosor@github.com/georgid/AlignmentServer.git
#RUN pip install -r $HOME/AlignmentServer/requirements/production.txt


# HTK
WORKDIR $HOME
RUN \
    git clone https://github.com/loretoparisi/htk.git && \
    cd $HOME/htk && \
    ./configure --disable-hslab && \
    make all && \
    make install


# TODO: pdnn # @see https://www.cs.cmu.edu/~ymiao/pdnntk.html
#WORKDIR $HOME
#RUN git clone -b python3 https://github.com/georgid/pdnn.git

# postgres
RUN apt-get install -y postgresql postgresql-contrib


# env
ENV PYTHONPATH $HOME/pdnn:$PYTHONPATH

EXPOSE 8000

# needed because /usr/local/bin path is hardcoded in code
RUN ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg 


CMD ["bash"]
