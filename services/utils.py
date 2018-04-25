from urllib.request import urlopen
import os
import subprocess


def update_filename(instance, filename):
    return 'lyrics/{}'.format(instance.id)


def get_file(recording_url, alignment_id, output_dir):
    pass
    # if not os.path.isdir(output_dir):
    #     os.mkdir(output_dir)
    # # TODO: get automatically file type
    # source_file_uri = os.path.join(output_dir, alignment_id + '.mp3')
    # response = urlopen(recording_url)
    # a = response.read()
    # with open(source_file_uri, 'wb') as f:
    #     f.write(a)
    #
    # wav_file_uri = os.path.join(output_dir, alignment_id + '.wav')
    # if os.path.isfile(wav_file_uri):
    #     return
    #
    # pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', source_file_uri, wav_file_uri])
    # pipe.wait()
