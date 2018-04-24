from rest_framework import serializers
from .models import Alignment
from composition.models import Composition
from services import exceptions
from django.core.validators import URLValidator
from django.db import IntegrityError, transaction
from rest_framework.exceptions import NotFound


class AlignmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    accompaniment = serializers.IntegerField(required=True)
    level = serializers.IntegerField(required=False)
    composition_id = serializers.CharField(max_length=100, required=False, default=None)
    lyrics = serializers.FileField(required=False)

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

        if self.validated_data.get('lyrics', None):
            lyrics = validated_data.pop('lyrics')

            try:
                with transaction.atomic():
                    if self.validated_data.get('title', None):
                        composition_object = Composition.objects.create(lyrics=lyrics, title=validated_data.pop('title'))
                    else:
                        composition_object = Composition.objects.create(lyrics=lyrics)
            except IntegrityError as e:
                raise e.message

        elif self.validated_data.get('composition_id', None):
            try:
                composition_object = Composition.objects.get(id=validated_data.pop('composition_id'))
            except Exception:
                raise exceptions.CompositionException

        else:
            raise exceptions.DataNotProvided

        if self.validated_data.get('level', None):
            alignment = Alignment.objects.create(composition=composition_object, accompaniment=accompaniment, level=validated_data.pop('level'))
        else:
            alignment = Alignment.objects.create(composition=composition_object, accompaniment=accompaniment)

        return alignment

    def to_representation(self, instance):
        """

        :param instance:
        :return: dict values

        """
        return {'alignment_id': instance.id, 'composition_id': instance.composition_id}


class AlignmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alignment
        fields = '__all__'


class UploadAudioSerializer(serializers.Serializer):
    recording_url = serializers.URLField(required=True)
    alignment_id = serializers.IntegerField(required=True)

    class Meta:
        fields = ['url', 'alignment_id']

    def validated_url(value):
        try:
            validator = URLValidator()
            validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError('Please enter a valid URL.')
        return value

    def validated_alignment_id(value):
        try:
            Alignment.objects.get(id=value)

        except Alignment.DoesNotExist:
            raise 'Alignment does not exist'
        return value
