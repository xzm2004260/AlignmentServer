from rest_framework import serializers
from .models import Alignment
from composition.models import Composition
from services import exceptions
from django.core.validators import URLValidator
from django.db import IntegrityError, transaction
from rest_framework.exceptions import NotFound
from django.core.files.uploadedfile import InMemoryUploadedFile
import io


class AlignmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    accompaniment = serializers.IntegerField(required=True)
    level = serializers.IntegerField(required=False)
    composition_id = serializers.CharField(max_length=100, required=False, default=None)
    lyrics_file = serializers.FileField(required=False)
    lyrics_text = serializers.CharField(min_length=15, required=False)

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

        if self.validated_data.get('lyrics_file', None) or self.validated_data.get('lyrics_text', None):
            if self.validated_data.get('lyrics_file', None):
                lyrics_file = validated_data.pop('lyrics_file')

                try:
                    with transaction.atomic():
                        if self.validated_data.get('title', None):
                            composition_object = Composition.objects.create(lyrics=lyrics_file,
                                                                            title=validated_data.pop('title'))
                        else:
                            composition_object = Composition.objects.create(lyrics=lyrics_file)
                except IntegrityError as e:
                    raise e.message
            else:
                lyrics_text = validated_data.pop('lyrics_text')
                # lyrics_text = "hello\nworld\nthere!"
                lyrics_text_encoded = lyrics_text.encode('latin-1')
#                 lines = lyrics_text_encoded.split('\n')
                file_data = io.StringIO()
                len_ = file_data.write(lyrics_text)
                file_stream = InMemoryUploadedFile(file_data, None, 'test.txt', 'text', len_, None)

                try:
                    with transaction.atomic():
                        if self.validated_data.get('title', None):
                            composition_object = Composition.objects.create(
                                lyrics=file_stream,
                                title=validated_data.pop('title')
                            )
                            file_stream.close()
                        else:
                            composition_object = Composition.objects.create(lyrics=file_stream)
                            file_stream.close()
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
        fields = ['recording_url', 'alignment_id']

    def validate_recording_url(self, value):
        try:
            validator = URLValidator()
            validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError('Please enter a valid URL.')
        return value

    def validate_alignment_id(self, value):
        try:
            Alignment.objects.get(id=value)

        except Exception:
            raise exceptions.AlignmentException
        return value
