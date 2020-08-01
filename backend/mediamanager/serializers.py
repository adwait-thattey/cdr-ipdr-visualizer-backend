from rest_framework import serializers

from mediamanager.models import MediaManager


class MediaManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaManager
        fields = ('id', 'title', 'type', 'media_file', 'url', 'created_date', 'modified_date')
        read_only_fields = ('id', 'url', 'created_date', 'modified_date')
