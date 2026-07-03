from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

class ServiceManageSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "is_active",
        )

    def validate_name(self, value):

        queryset = Service.objects.filter(name__iexact=value)

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                "Service already exists."
            )

        return value

    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters long."
            )
        return value