from django.utils import timezone
from rest_framework import serializers

from .models import PlatformUser


class PlatformUserSerializer(serializers.ModelSerializer):
    user_eid = serializers.SerializerMethodField()

    class Meta:
        model = PlatformUser
        fields = (
            'name',
            'phone',
            'is_active',
            'user_eid'
        )

    def get_user_eid(self, obj):
        return obj.get_user_external_id()
