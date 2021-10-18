from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_pos_num(value):
    """
    Validator to ensure that a numeric field is positive. If it's the case, add a ValidationError.
    """
    raise_error = False
    try:
        if float(value) <= 0:
            raise_error = True
    except ValueError:
        raise_error = True
    if raise_error:
        raise ValidationError(
            _('Attention, la valeur doit être un nombre positif (ex: 21.32)'),
            params={'value': value},
            code='negative'
        )
