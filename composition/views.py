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
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = CompositionSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
