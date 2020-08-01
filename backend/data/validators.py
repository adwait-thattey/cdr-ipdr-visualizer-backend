from django.core.exceptions import ValidationError


def mobile_validation(mobile):
    mobile = str(mobile)

    if len(mobile) < 10 or not mobile.isdecimal() or mobile[0] == '0':
        raise ValidationError("Invalid Mobile NUmber")

    return mobile
