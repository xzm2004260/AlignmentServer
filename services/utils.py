try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import os
import subprocess


def update_filename(instance, filename):
    return 'lyrics/{}'.format(instance.id)


def get_file(recording_URL, alignment_id,  outputDir):
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    # TODO: get automatically file type
    source_file_URI = os.path.join(outputDir, alignment_id + '.mp3')
    response = urlopen(recording_URL)
    a = response.read()
    with open(source_file_URI, 'w') as f:
        f.write(a)

    wav_file_URI = os.path.join(outputDir, alignment_id + '.wav')
    if os.path.isfile(wav_file_URI):
        return

    pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', source_file_URI, wav_file_URI])
    pipe.wait()
