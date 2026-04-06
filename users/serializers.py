import re
from django.utils import timezone
from rest_framework import serializers
from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "first_name", "last_name", "role",
                  "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]

    def validate_username(self, value):
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username must contain only alphanumeric characters and underscores."
            )
        return value

    def validate_password(self, value):
        errors = []
        if not re.search(r"[A-Z]", value):
            errors.append("at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            errors.append("at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            errors.append("at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("at least one special character")
        if errors:
            raise serializers.ValidationError("Password must contain " + ", ".join(errors) + ".")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name",
                  "role", "is_active", "created_at", "updated_at"]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "is_active"]

    def validate_email(self, value):
        qs = User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None)
        if qs.exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def validate_username(self, value):
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username must contain only alphanumeric characters and underscores."
            )
        qs = User.objects.filter(username=value).exclude(pk=self.instance.pk if self.instance else None)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value


class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Role.choices)
