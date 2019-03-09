#
# numpy, scipy, pdnn, and htk
# @author Georgi Dzhambazov
# v1.0.0
#
#
FROM ubuntu:16.04

MAINTAINER Georgi Dzhambazov <info@voicemagix.com>

# working directory
ENV HOME /root
ENV ALIGNMENT_MAGIX /homedtic/georgid/workspace/AlignmentMagix
WORKDIR $HOME


# packages list
RUN \
	apt-get update && apt-get install -y \
    libx11-dev \
    gawk \
    python-dev \
    python-pip \
    curl \
    git

# pip
RUN pip install --upgrade pip

# copy & install compat-gcc-34-c++ compat-gcc-34
#COPY lib/*.deb $HOME/
#RUN \
#    dpkg -i $HOME/compat-gcc-34-c++_3.4.6-20_amd64.deb && \
#    dpkg -i $HOME/compat-gcc-34-c++_3.4.6-20_amd64.deb


# essentia 
RUN apt-get install -y libyaml-0-2 libfftw3-3 libtag1v5 libsamplerate0 \
libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 \
libavresample-ffmpeg2 python python-numpy libpython2.7 python-numpy python-yaml python-six

RUN apt-get install -y build-essential libyaml-dev libfftw3-dev \
libavcodec-dev libavformat-dev libavutil-dev libavresample-dev \
python-dev libsamplerate0-dev libtag1-dev python-numpy-dev git

RUN git clone -b pabloEntropia-viterbi-forced https://github.com/georgid/essentia
RUN python ./waf configure --with-python --include-algos=MelBands,TriangularBands,DCT,MFCC,FrameCutter,Viterbi,FileOutputProxy --arch=x64 --pythondir=/usr/local/lib/python2.7/site-packages/
RUN sudo python ./waf install

# theano and lasagne
# RUN pip install theano
# RUN pip install https://github.com/Lasagne/Lasagne/archive/master.zip # last working version of Lasagne

# utility dependencies
cd $ALIGNMENT_MAGIX
RUN pip install -r requirements
cd $ALIGNMENT_MAGIX/../
RUN pip install -e git+https://github.com/pwdyson/inflect.py#egg=inflect; cd inflect; python setup.py install

# HTK
RUN \
    git clone https://github.com/loretoparisi/htk.git && \
    cd $HOME/htk && \
    ./configure --disable-hslab && \
    make all && \
    make install

# pdnn
# @see https://www.cs.cmu.edu/~ymiao/pdnntk.html
cd $ALIGNMENT_MAGIX/../
RUN git clone https://github.com/yajiemiao/pdnn

# env
ENV PYTHONPATH $ALIGNMENT_MAGIX/../pdnn:$PYTHONPATH

CMD ["bash"]
