from rest_framework import serializers

from .models import CorpusData


class CorpusDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorpusData
        fields = ['file_type', 'content', 'status']
