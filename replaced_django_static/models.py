from django.db import models


# Create your models here.

base_float_init = models.FloatField.__init__
base_float_prep_value = models.FloatField.get_prep_value
base_float_to_python = models.FloatField.to_python


def new_float_init(self, *args, **kwargs):
    self.use_round = kwargs.pop('use_round', False)
    base_float_init(self, *args, **kwargs)


def new_float_prep_value(self, *args, **kwargs):
    result = base_float_prep_value(self, *args, **kwargs)
    if result is None or not self.use_round:
        return result

    return round(result, 4)


def new_float_to_python(self, *args, **kwargs):
    result = base_float_to_python(self, *args, **kwargs)
    if result is None or not self.use_round:
        return result

    return round(result, 4)


models.FloatField.__init__ = new_float_init
models.FloatField.get_prep_value = new_float_prep_value
models.FloatField.to_python = new_float_to_python
