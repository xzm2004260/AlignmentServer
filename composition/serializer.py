from rest_framework import serializers
from .models import Composition
from alignment.models import Alignment


class CompositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Composition
        fields = '__all__'
        extra_kwargs = {
            'lyrics': {'write_only': True},
            'title': {'write_only': True}
        }

    def create(self, validated_data):
        composition_object = Composition.objects.create(**validated_data)
        Alignment.objects.create(compositions=composition_object)
        return composition_object
