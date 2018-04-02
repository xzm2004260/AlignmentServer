from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from .serializer import AlignmentSerializer
from .models import Alignment


class CreateAlignmentAPIView(APIView):

    """
        POST:
        Create a new alignment instance.

    """

    def post(self, request, format=None):
        serializer = AlignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        serializer = AlignmentSerializer(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)
