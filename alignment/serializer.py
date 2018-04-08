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
        alignment = Alignment.objects.create(composition=composition_object)
        return alignment

    def to_representation(self, instance):
        """

        :param instance:
        :return: dict values

        """
        return {'alignment_id': instance.id, 'lyrics_id': instance.composition_id}