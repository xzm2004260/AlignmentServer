from rest_framework import serializers
from .models import Composition
from alignment.models import Alignment


class CompositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Composition
        fields = '__all__'
