from urllib.request import urlopen
from urllib.error import HTTPError
import os
import subprocess
import sys
import re
# from django.db import IntegrityError, transaction


def update_filename(instance, filename):
    return 'lyrics/{}'.format(instance.id)
#
# def composition_creation(self, file):
#     try:
#         with transaction.atomic():
#             if self.validated_data.get('title', None):
#                 composition_object = Composition.objects.create(
#                     lyrics=file,
#                     title=self.validated_data.pop('title')
#                 )
#             else:
#                 composition_object = Composition.objects.create(lyrics=file)
#             return composition_object
#     except IntegrityError as e:
#         raise e.message

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

    # url = "https://flowra-.com/5b23e1cf6ba8f0282d19039c.mps/AWSAccessKeyId=AKIAIOV6UBGWVLCNHMNA&Expires=1529087597&Signature=TrZ5Whn4iHF9mFpaO56f%2BYwQGgk%3D"
    stripped_url = recording_url.strip()
    extensions = ['mp3', 'wav', 'mp4', 'm4a', 'ogg']  # here  are some supported by ffmpeg
    splitted_url = re.split(r'[\@#%&+\[\];\'\\:"|<,./<>?]', stripped_url)
    extension_file = None
    for ext in extensions:
        if ext in splitted_url:
            extension_file = ext
            
    if extension_file == None: # if name not in list, we have no audio in URL
       raise RuntimeError("None of the expected file extensions (.mp3, .ogg etc.) for audio found in given URL")
    
    try:            
        response = urlopen(recording_url)
    except HTTPError as err:
        if err.code == 403: # we care to inform the user for this type of error that happens on signed urls
            msg = 'The given url is forbidden. Are you sure you are authorized to access it?' 
        else:
            msg = err.reason
        raise RuntimeError(msg)
 
    a = response.read()
    
#     a = urlretrieve(recording_url)    

    source_file_uri = os.path.join(output_dir, alignment_id + '.' + extension_file)
    with open(source_file_uri, 'wb') as f:
        f.write(a)

#     shutil.copy(recording_url, source_file_uri)
    
    recording_URI = os.path.join(output_dir, alignment_id + '.wav')
    pipe = subprocess.check_call(['/usr/local/bin/ffmpeg', '-y', '-i', source_file_uri, recording_URI]) # convert to wav
#     pipe.wait()
    
    return recording_URI
