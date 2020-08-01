from django.db import models
from django.contrib.postgres.fields import JSONField

from data.validators import mobile_validation
from uuid import uuid4


class Person(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField(max_length=300, default="", blank=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class MobileNumber(models.Model):
    number = models.CharField(max_length=10, unique=True)
    last_known_location = JSONField(null=True, blank=True, default=None)

    associated_person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None, related_name="mobile_numbers",
                                          blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.associated_person is None:
            person = Person(name=f"Mobile : {self.mobile} (Unknown person)")
            person.save()
            self.associated_person = person

        super().save(*args, **kwargs)

    def clean(self):
        self.mobile = mobile_validation(self.mobile)

    def __str__(self):
        return f"{self.mobile} : {self.associated_person}"


class SimCard(models.Model):
    mobile_number = models.ForeignKey(to=MobileNumber, on_delete=models.CASCADE)
    imsi = models.CharField(max_length=20, db_index=True)


class Device(models.Model):
    mobile_numbers = models.ManyToManyField(to=MobileNumber, blank=True, db_index=True)
    imei = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    mac = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    persons = models.ForeignKey(to=Person, on_delete=models.CASCADE, null=True, blank=True, db_index=True)


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
    start_time = models.DateField(null=True, blank=True, db_index=True)
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

    upload_data_volume = models.BigIntegerField(null=True, blank=True, db_index=True)
    download_data_volume = models.BigIntegerField(null=True, blank=True, db_index=True)
