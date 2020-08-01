from rest_framework import serializers

from .models import Person, MobileNumber, Device, SimCard, CDR, IPDR


class MinimalCDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDR
        fields = ('id',)
        read_only_fields = ('id',)


class FullCDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDR
        fields = '__all__'


class MinimalIPDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPDR
        fields = ('id',)
        read_only_fields = ('id',)


class FullIPDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPDR
        fields = '__all__'



