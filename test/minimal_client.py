import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os

PATH_TEST = os.path.dirname(os.path.realpath(__file__)) 

url = "http://127.0.0.1:8000/alignments/"
f = open(os.path.join(PATH_TEST, 'data/umbrella_line.txt'), 'rb')

alignment_data = MultipartEncoder(
    fields={
            # a file upload field
            'lyrics': ('test_long_lyrics.txt', f, 'text/plain'),
            # plain text fields
            'title': 'new composition', 
            'accompaniment': '2',
            'level':'1'

           }
    )


response = requests.post(url, data=alignment_data, headers={'Content-Type': alignment_data.content_type})
response.raise_for_status()
print(response.text)