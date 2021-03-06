import os

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import NotFound
from .serializer import (
    AlignmentSerializer,
    AlignmentDetailSerializer,
    UploadAudioSerializer
)
from .models import Alignment
from services.utils import get_file
from services.authentication import UserAuthentication

settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')


if settings_name == 'config.settings.debug':
    from config.settings import debug as settings
elif settings_name == 'config.settings.production':
    from config.settings import production as settings


from alignment.thread_alignment import AlignThread


class CreateAlignmentAPIView(APIView):

    """
    POST:
        Create a new alignment with composition instance.

    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = AlignmentSerializer
    if not settings.DEBUG:
        permission_classes = (permissions.IsAuthenticated,)
        authentication_classes = (UserAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlignmentDetailAPIView(APIView):
    """
    GET:
       Get an existing alignment instance against some id.

    """
    if not settings.DEBUG:
        permission_classes = (permissions.IsAuthenticated,)
        authentication_classes = (UserAuthentication,)

    def get_object(self):
        try:
            return Alignment.objects.get(id=self.kwargs.get('pk'))
        except Alignment.DoesNotExist:
            raise NotFound

    def get(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        serializer = AlignmentDetailSerializer(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)


class UploadAPIView(APIView):

    """
    POST:
        Get a new audio instance.

    """
    if not settings.DEBUG:
        permission_classes = (permissions.IsAuthenticated,)
        authentication_classes = (UserAuthentication,)

    def post(self, request):

        serializer = UploadAudioSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            recording_url = request.data['recording_url']
            alignment_id = request.data['alignment_id']
#             dir_path = os.path.dirname(os.path.realpath(__file__))
            output_dir = os.path.join(settings.MEDIA_ROOT, 'recordings/')
            try:
                recording_URI = get_file(recording_url, alignment_id, output_dir) # upload audio to server from recording URL
            except (RuntimeError) as error:
                print(error)
                return Response(str(error), status=status.HTTP_404_NOT_FOUND)

            align_thread = AlignThread(alignment_id, recording_URI) 
            align_thread.start()
            return Response("Audio uploaded successfully", status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

