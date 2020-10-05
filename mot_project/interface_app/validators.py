from django.core.exceptions import ValidationError


def is_pos_num(value):
    raise_error = False
    try:
        if float(value) <= 0: raise_error = True
    except ValueError:
        raise_error = True
    if raise_error:
        raise ValidationError(
            'Attention, la valeur doit être un nombre positif (ex: 21.32)',
            params={'value': value},
            code='negative'
        )
