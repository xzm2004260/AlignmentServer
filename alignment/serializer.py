from rest_framework import serializers
from .models import Alignment
from composition.models import Composition
from rest_framework import status
from services import exceptions
from django.db import IntegrityError, transaction


class AlignmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    accompaniment = serializers.IntegerField(required=True)
    level = serializers.IntegerField(required=False)
    composition_id = serializers.UUIDField(required=False, default=None)
    lyrics = serializers.FileField(required=True)

    class Meta:
        fields = '__all__'

    @staticmethod
    def validate_accompaniment(value):
        """

        :param value:
        :return: validated accompaniment value

        """
        if not value in range(1, 3):
            raise serializers.ValidationError(
                "{} is not a valid accompaniment. please enter 1=ACAPELLA or 2=MULTIINSTRUMENTAL"
                .format(value))
        return value

    @staticmethod
    def validate_level(value):
        """

        :param value:
        :return: validated level field

        """
        if not value in range(1, 3):
            raise serializers.ValidationError(
                "{} is not a valid level. please enter 1=WORDS or 2=LINES"
                .format(value))
        return value

    def create(self, validated_data):
        accompaniment = validated_data.pop('accompaniment')
        level = validated_data.pop('level') if validated_data['level'] else None

        if validated_data['lyrics']:
            title = validated_data.pop('title') if validated_data['title'] else None
            lyrics = validated_data.pop('lyrics')

            try:
                with transaction.atomic():
                    composition_object = Composition.objects.create(lyrics=lyrics, title=title)
            except IntegrityError as e:
                raise e.message

        elif validated_data['composition_id']:
            try:
                composition_object = Composition.objects.get(id=validated_data['composition_id'])

            except Alignment.DoesNotExist:
                return status.HTTP_404_NOT_FOUND

        else:
            raise exceptions.DataNotProvided

        alignment = Alignment.objects.create(composition=composition_object, accompaniment=accompaniment, level=level)
        return alignment






    def to_representation(self, instance):
        """

        :param instance:
        :return: dict values

        """
        return {'alignment_id': instance.id, 'lyrics_id': instance.composition_id}


class AlignmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alignment
        fields = '__all__'
