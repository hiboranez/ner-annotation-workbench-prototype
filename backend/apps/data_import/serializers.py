from rest_framework import serializers

from .models import CorpusData


class CorpusDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorpusData
        fields = ['id', 'fileType', 'original_filename', 'content', 'status', 'created_at']
