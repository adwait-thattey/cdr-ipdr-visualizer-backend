from rest_framework import serializers

from .models import Person, MobileNumber, Device, SimCard, CDR, IPDR


class PersonFullSerializer(serializers.ModelSerializer):
    phone_numbers = serializers.SerializerMethodField()
    devices = serializers.SerializerMethodField()

    def get_devices(self, obj: Person):
        devices = obj.device_set.all()
        device_data = []
        for d in devices:
            if d.imei:
                device_data.append({'imei': d.imei})
            elif d.mac:
                device_data.append(({'mac': d.mac}))

        return device_data

    def get_phone_numbers(self, obj: Person):
        mobiles = obj.mobile_numbers.all()
        mobiles_data = []
        for m in mobiles:
            sims = [m.simcard_set.all().values_list('imsi', flat=True)]
            mobiles_data.append({m.number: sims})

        return mobiles_data

    class Meta:
        model = Person
        fields = ('id', 'name', 'address', 'phone_numbers', 'devices')


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
