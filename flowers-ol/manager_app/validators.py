from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def _is_number(x):
    try:
        # only integers and float converts safely
        num = float(x)
        return True
    except ValueError as e: # not convertable to float
        return False


def validate_session_stack(value):
    no_spaces = value.replace(' ', '')
    for i in no_spaces.split(','):
        if not i.isdigit():
            raise ValidationError((f'Session stack is not a valide csv string. Check how session stack is creater or assigned'))


def validate_timedelta_args(value):
    if value:
        legal_keys = ['days','minutes']
        problems = []
        problems.append(len(value) > 1) # check if more than 1 key-value pair is passed
        for k, v in value.items():
            problems.append(k not in legal_keys) # check if key is illegal
            problems.append(not _is_number(v)) # check if value is not an int
            if not problems[-1]: 
                problems.append(v <= 0) # if value is int, check if negative
        if any(problems):
            raise ValidationError('this is a JSON field that must have at most 1 key-value pair; key must be either \"days\" or \"minutes\" (case-sensitive); value must be positive nonzero number')
