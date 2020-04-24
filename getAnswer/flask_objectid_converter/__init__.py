from bson.objectid import ObjectId, InvalidId

from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode


class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)

        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return str(value)


class Base64ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value))

        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return base64_encode(value.binary).decode('utf-8')