from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializer import AlignmentSerializer


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
