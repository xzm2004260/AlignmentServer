from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializer import CompositionSerializer


class CompositionCreateAPIView(APIView):

    """
        POST:
        Create a new composition instance.

    """
