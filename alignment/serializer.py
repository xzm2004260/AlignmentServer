from rest_framework import serializers
from .models import Alignment
from composition.models import Composition


class AlignmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    lyrics = serializers.FileField(required=True)

    class Meta:
        fields = '__all__'

    def create(self, validated_data):

        title = validated_data.pop('title')
        lyrics = validated_data.pop('lyrics')
        composition_object = Composition.objects.create(lyrics=lyrics, title=title)
        alignment = Alignment.objects.create(compositions=composition_object)
        return alignment

    def to_representation(self, instance):
        """

        :param instance:
        :return: dict values

        """
        return {'id': instance.id, 'composition': instance.compositions_id}