from rest_framework import serializers

from .models import Person, MobileNumber, Device, SimCard, CDR, IPDR, WatchList, Service, Alert, AlertInstance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


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


class WatchListSerializer(serializers.ModelSerializer):
    users_list = serializers.SerializerMethodField()

    def get_users_list(self, obj):
        users = [int(i) for i in obj.users_list.split(',') if i]
        return users

    class Meta:
        model = WatchList
        fields = '__all__'
        read_only_fields = ('id', 'users_list')


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"
        read_only_fields = ('id',)


class AlertInstanceSerializer(serializers.ModelSerializer):
    alert = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()
    instance = serializers.SerializerMethodField()

    def get_alert(self, obj):
        ass = AlertSerializer(obj.alert)
        return ass.data

    def get_object(self, obj):
        to = obj.tracked_obj
        return {'attribute': to.attribute, 'value': to.value}

    def get_instance(self, obj:AlertInstance):
        if obj.cdr_instance:
            cdr_obj = CDR.objects.filter(id=obj.cdr_instance)
            if cdr_obj.exists():
                cdr_ser = FullCDRSerializer(cdr_obj)
                return cdr_ser.data
        elif obj.ipdr_instance:
            ipdr_obj = IPDR.objects.filter(id=obj.ipdr_instance)
            if ipdr_obj.exists():
                ipdr_ser = FullIPDRSerializer(ipdr_obj)
                return ipdr_ser.data
        else:
            return {}

    class Meta:
        model = AlertInstance
        fields = ('id', 'timestamp', 'alert', 'object', 'instance')


