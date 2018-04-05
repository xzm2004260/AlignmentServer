from rest_framework import serializers
from .models import Alignment


class AlignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alignment
        fields = '__all__'
