from urllib.request import urlopen
import os
import subprocess
import sys


def update_filename(instance, filename):
    return 'lyrics/{}'.format(instance.id)


def get_file(recording_url, alignment_id, output_dir):
    '''
    fetch the audio file from a remote url, 
    rename to id of its related alignment,
    transcode to wav
    
    
    Parameters
    -----
    recording_url: str
        the url of the audio file
    alignment_id: int
        the id of the recording to which the audio refers
    
    '''
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    
    # TODO: get automatically file type
    ext = os.path.splitext(recording_url)[1]
    if ext not in ['.mp3', '.wav', '.mp4', '.m4a','.ogg']: # all that are supported by ffmpeg
        sys.exit('not acceptable extension') 
    source_file_uri = os.path.join(output_dir, alignment_id + ext)
    response = urlopen(recording_url)
    a = response.read()
    with open(source_file_uri, 'wb') as f:
        f.write(a)
    
    recording_URI = os.path.join(output_dir, alignment_id + '.wav')
    pipe = subprocess.check_call(['/usr/local/bin/ffmpeg', '-y', '-i', source_file_uri, recording_URI])
#     pipe.wait()
    
    return recording_URI
