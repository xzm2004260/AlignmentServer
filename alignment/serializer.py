from rest_framework import serializers
from .models import Alignment
from composition.models import Composition
from composition.serializer import CompositionSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST


class AlignmentSerializer(serializers.ModelSerializer):
    # composition = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Alignment
        # fields = ['id', 'created_at', 'composition']
        fields = '__all__'
    # def create(self, validated_data):
    #     # obj = Composition.objects.get(id=composition_id)
    #     alignment = Alignment.objects.create(composition=self.data['pk'])
    #     alignment.save()
    #     return alignment


