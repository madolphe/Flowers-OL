from django.core.exceptions import ValidationError


def dummy(value):
    pass


def is_pos_num(value):
    raise_error = False
    try:
        if float(value) <= 0: raise_error = True
    except ValueError:
        raise_error = True
    if raise_error:
        raise ValidationError(
            ('Value must be a positive number'),
            params={'value': value},
        )
