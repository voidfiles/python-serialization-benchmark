from django.conf import settings
settings.configure()

import django
django.setup()

from rest_framework import serializers as rf_serializers

name = 'Django REST Framework'


class SubRF(rf_serializers.Serializer):
    w = rf_serializers.IntegerField()
    x = rf_serializers.SerializerMethodField()
    y = rf_serializers.CharField()
    z = rf_serializers.IntegerField()

    def get_x(self, obj):
        return obj.x + 10


class ComplexRF(rf_serializers.Serializer):
    foo = rf_serializers.CharField()
    bar = rf_serializers.IntegerField()
    sub = SubRF()
    subs = SubRF(many=True)


def serialize_func(obj, many):
    return ComplexRF(obj, many=many).data


def deserialize_func(obj, many):
    return ComplexRF(data=obj, many=many).is_valid()
