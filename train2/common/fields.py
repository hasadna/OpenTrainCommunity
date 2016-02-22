from django.db import models
import json


class ArrayField(models.TextField):

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        result = json.loads(value)
        if not isinstance(result,list):
            raise ValueError('value should be of type list')
        return result

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return value
        result = json.loads(value)
        if not isinstance(result,list):
            raise ValueError('value should be of type list')
        return result

    def get_prep_value(self, value):
        if value is None:
            return None
        return json.dumps(value)




