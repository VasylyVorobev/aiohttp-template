from marshmallow import Schema
from marshmallow.fields import Bool


class PingSchema(Schema):
    detail: bool = Bool()
