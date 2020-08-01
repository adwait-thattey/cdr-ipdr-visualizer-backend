from django.db import models
from django.contrib.postgres.fields import JSONField

from data.validators import mobile_validation
from uuid import uuid4


class Person(models.Model):
    name = models.CharField(max_length=50)
    pkk = models.UUIDField(unique=True, default=uuid4, name="UUID")
    address = models.TextField(max_length=300, default="", blank=True)
    suspect_level = models.DecimalField(null=True, blank=True, default=None, max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.pkk}"


class Mobile(models.Model):
    mobile = models.CharField(max_length=10, unique=True)
    last_known_location = JSONField(null=True, blank=True, default=None)

    associated_person = models.ForeignKey(Person, on_delete=models.SET_DEFAULT, default=None, related_name="mobiles",
                                          blank=True, null=True)

    person_ptr = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="is_mobile", editable=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            person = Person(name=f"Mobile - {self.mobile}", suspect_level=None)
            person.save()
            self.person_ptr = person
        if self.associated_person is None:
            self.associated_person = self.person_ptr
        super().save(*args, **kwargs)

    def clean(self):
        self.mobile = mobile_validation(self.mobile)

    def __str__(self):
        return f"{self.mobile} : {self.associated_person}"
