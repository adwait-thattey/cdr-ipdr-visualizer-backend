from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import signals
from django.dispatch import receiver

from data.validators import mobile_validation
from uuid import uuid4


class Person(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField(max_length=300, default="", blank=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class MobileNumber(models.Model):
    number = models.CharField(max_length=20, unique=True)
    last_known_location = JSONField(null=True, blank=True, default=None)

    associated_person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None, related_name="mobile_numbers",
                                          blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.associated_person is None:
            person = Person(name=f"Mobile : {self.number} (Unknown person)")
            person.save()
            self.associated_person = person

        super().save(*args, **kwargs)

    def clean(self):
        self.mobile = mobile_validation(self.mobile)

    def __str__(self):
        return f"{self.number} : {self.associated_person}"


class SimCard(models.Model):
    mobile_number = models.ForeignKey(to=MobileNumber, on_delete=models.CASCADE)
    imsi = models.CharField(max_length=20, db_index=True)


class Device(models.Model):
    mobile_numbers = models.ManyToManyField(to=MobileNumber, blank=True, db_index=True)
    imei = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    mac = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, null=True, blank=True, db_index=True)


class Service(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    ip = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    port = models.IntegerField(null=True, blank=True, db_index=True)


class CDR(models.Model):
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True)
    from_number = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    to_number = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    duration = models.IntegerField(null=True, blank=True, db_index=True)
    call_type = models.CharField(max_length=20, default="outgoing call", null=True, blank=True, db_index=True)
    imei = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    imsi = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    cell_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    location_lat = models.FloatField(null=True, blank=True, db_index=True)
    location_long = models.FloatField(null=True, blank=True, db_index=True)

    def clean(self):
        self.call_type = self.call_type.lower()


class IPDR(models.Model):
    start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    duration = models.IntegerField(null=True, blank=True, db_index=True)

    private_ip = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    private_port = models.IntegerField(null=True, blank=True, db_index=True)
    public_ip = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    public_port = models.IntegerField(null=True, blank=True, db_index=True)
    destination_ip = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    destination_port = models.IntegerField(null=True, blank=True, db_index=True)

    from_number = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    imei = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    imsi = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    cell_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    location_lat = models.FloatField(null=True, blank=True, db_index=True)
    location_long = models.FloatField(null=True, blank=True, db_index=True)

    upload_data_volume = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    download_data_volume = models.CharField(max_length=100, null=True, blank=True, db_index=True)


@receiver(signals.post_save, sender=IPDR)
def associated_ipdr(sender, instance: IPDR, **kwargs):
    from_num = instance.from_number
    imei = instance.imei
    imsi = instance.imsi

    from_mobile = MobileNumber.objects.filter(number=from_num)

    if from_mobile.exists():
        from_mobile = from_mobile[0]
        simcard = SimCard.objects.filter(imsi=imsi)
        if not simcard.exists() and imsi:
            simcard = SimCard.objects.create(mobile_number=from_mobile, imsi=imsi)
    else:
        from_mobile = MobileNumber.objects.create(number=from_num)
        if imsi:
            simcard = SimCard.objects.create(mobile_number=from_mobile, imsi=imsi)

    device = Device.objects.filter(imei=imei)
    if device.exists():
        device = device[0]
    elif imei:
        device = Device.objects.create(imei=imei)
    else:
        device = None
    # print(device.mobile_numbers.all())
    found_person = None
    if device and device.person:
        found_person = device.person
    # print(device.mobile_numbers.all())
    if from_mobile.associated_person.name[:6].lower() == "mobile":
        if found_person:
            from_mobile.associated_person = found_person
            from_mobile.save()
        if not found_person and device:
            device.person = from_mobile.associated_person
            device.save()
    else:
        if not found_person and device:
            device.person = from_mobile.associated_person
            device.save()

    if device:
        device.mobile_numbers.add(from_mobile)

    services = Service.objects.filter(ip=instance.destination_ip)
    if services.exists():
        port_filtered_services = services.filter(port=instance.destination_port)
        if port_filtered_services.exists():
            pass
        else:
            Service.objects.create(name=services[0].name, ip=instance.destination_ip,
                                   port=instance.destination_port)
    else:
        Service.objects.create(name=f"unknown service at {instance.destination_ip}", ip=instance.destination_ip,
                               port=instance.destination_port)


@receiver(signals.post_save, sender=CDR)
def create_associated_mobile_numbers(sender, instance: CDR, **kwargs):
    from_num = instance.from_number
    to_num = instance.to_number
    imei = instance.imei
    imsi = instance.imsi

    from_mobile = MobileNumber.objects.filter(number=from_num)
    to_mobile = MobileNumber.objects.filter(number=to_num)

    if from_mobile.exists():
        from_mobile = from_mobile[0]
        simcard = SimCard.objects.filter(imsi=imsi)
        if not simcard.exists() and imsi:
            simcard = SimCard.objects.create(mobile_number=from_mobile, imsi=imsi)
    else:
        from_mobile = MobileNumber.objects.create(number=from_num)
        if imsi:
            simcard = SimCard.objects.create(mobile_number=from_mobile, imsi=imsi)
    if to_mobile.exists():
        to_mobile = to_mobile[0]
    else:
        to_mobile = MobileNumber.objects.create(number=to_num)

    device = Device.objects.filter(imei=imei)
    if device.exists():
        device = device[0]
    elif imei:
        device = Device.objects.create(imei=imei)
    else:
        device = None
    # print(device.mobile_numbers.all())
    found_person = None
    if device and device.person:
        found_person = device.person
    # print(device.mobile_numbers.all())
    if from_mobile.associated_person.name[:6].lower() == "mobile":
        if found_person:
            from_mobile.associated_person = found_person
            from_mobile.save()
        if not found_person and device:
            device.person = from_mobile.associated_person
            device.save()
    else:
        if not found_person and device:
            device.person = from_mobile.associated_person
            device.save()

    if device:
        device.mobile_numbers.add(from_mobile)

    # else:
    # if device.person != from_mobile.associated_person:
    #     Anomaly.objects.create(text=f"New number {from_num} found on IMEI {imei} which was previously on number {device.mobile_numbers}")

    # print(device.mobile_numbers.all())


class TrackedObject(models.Model):
    attribute = models.CharField(max_length=20, db_index=True)
    value = models.CharField(max_length=100, db_index=True)


def process_watchlist_raw_data(data):
    lines = [l.strip() for l in data.split('\n')]
    persons = list()
    for l in lines:
        try:
            t, val = l.split(',')
            t = t.lower()
            TrackedObject.objects.create(attribute=t, value=val)

            if t == "user_id" or t == "user":
                p = Person.objects.filter(id=int(val))
                if p.exists():
                    persons.append(p[0])
            elif t in ["phone", "number", "mobile", "mobile_number"]:
                mob = MobileNumber.objects.filter(number=val)
                if mob.exists():
                    mob = mob[0]
                    if mob.associated_person:
                        print(mob.associated_person)
                        persons.append(mob.associated_person)
            elif t == "imei":
                device = Device.objects.filter(imei=val)
                if device.exists():
                    device = device[0]
                    if device.person:
                        print(device.person)
                        persons.append(device.person)
            elif t == "mac":
                device = Device.objects.filter(mac=val)
                if device.exists():
                    device = device[0]
                    if device.person:
                        print(device.person)
                        persons.append(device.person)
        except Exception as e:
            print(e)

    # print(persons)
    return persons


class WatchList(models.Model):
    name = models.CharField(max_length=200)
    users_list = models.CharField(max_length=500, null=True, blank=True)
    to_display = models.BooleanField(default=True)
    raw_data = models.TextField()

    def save(self, *args, **kwargs):
        instance = self
        ps = process_watchlist_raw_data(instance.raw_data)
        print(ps)
        instance.users_list = ",".join([str(p.id) for p in ps])
        super().save(*args, **kwargs)


# @receiver(signals.post_save, sender=WatchList)
# def add_persons_ref_into_watchlists(sender, instance: WatchList, **kwargs):
#     # instance.persons.clear()


class Alert(models.Model):
    name = models.CharField(max_length=300)
