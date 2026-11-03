from rest_framework import serializers
from turff_app.models import *

class TurffSerializer(serializers.ModelSerializer):

    class Meta:
        model=TurfDb
        fields="__all__"
        read_only_fields=['id',"created_at","updated_at"]

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model=BookingDb
        fields="__all__"
        read_only_fields=["id","created_at","updated_at","total_price","status"]