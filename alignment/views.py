from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from .serializer import AlignmentSerializer, AlignmentDetailSerializer
from .models import Alignment
from services.utils import get_file
import os


class CreateAlignmentAPIView(APIView):

    """
    POST:
        Create a new alignment with composition instance.

    """
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AlignmentSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlignmentDetailAPIView(APIView):
    """
    GET:
       Get an existing alignment instance against some id.

    """

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

    def post(self, request):

        recording_url = request.data['recording_URL']
        alignment_id = request.data['alignment_id']
        dir_path = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(dir_path, 'recordings/')
        get_file(recording_url, alignment_id, output_dir)

        return Response( status=status.HTTP_200_OK)

