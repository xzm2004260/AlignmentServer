from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from .serializer import (
    AlignmentSerializer,
    AlignmentDetailSerializer,
    UploadAudioSerializer
)
from .models import Alignment
from services.utils import get_file
from rest_framework import permissions
from services.permissions import IsOwnerOrReadOnly
from services.authentication import UserAuthentication
import os
from Magixbackend.settings import MEDIA_ROOT
from alignment.thread_alignment import AlignThread


class CreateAlignmentAPIView(APIView):

    """
    POST:
        Create a new alignment with composition instance.

    """
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AlignmentSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (UserAuthentication,)

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
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (UserAuthentication,)

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
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (UserAuthentication,)

    def post(self, request):

        serializer = UploadAudioSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            recording_url = request.data['recording_url']
            alignment_id = request.data['alignment_id']
#             dir_path = os.path.dirname(os.path.realpath(__file__))
            output_dir = os.path.join(MEDIA_ROOT, 'recordings/')
            get_file(recording_url, alignment_id, output_dir) # upload audio to server from recording URL
            align_thread = AlignThread(alignment_id) 
            align_thread.start()
            return Response("Audio uploaded successfully", status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

