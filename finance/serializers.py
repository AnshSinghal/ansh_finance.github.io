from decimal import Decimal

from rest_framework import serializers
from .models import FinancialRecord, RecordType


class RecordCreateSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))

    class Meta:
        model = FinancialRecord
        fields = ["id", "user_id", "amount", "type", "category", "date", "description",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "user_id", "created_at", "updated_at"]

    def validate_type(self, value):
        if value not in RecordType.values:
            raise serializers.ValidationError(f"Type must be one of {RecordType.values}.")
        return value


class RecordUpdateSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"), required=False)

    class Meta:
        model = FinancialRecord
        fields = ["amount", "type", "category", "date", "description"]

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class RecordResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = ["id", "user_id", "amount", "type", "category", "date", "description",
                  "created_at", "updated_at"]
        read_only_fields = fields


class SummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_records = serializers.IntegerField()


class CategoryBreakdownSerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=20, decimal_places=2)
    count = serializers.IntegerField()


class TrendPointSerializer(serializers.Serializer):
    period = serializers.CharField()
    income = serializers.DecimalField(max_digits=20, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=20, decimal_places=2)
    net = serializers.DecimalField(max_digits=20, decimal_places=2)


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    type = serializers.CharField()
    category = serializers.CharField()
    date = serializers.DateField()
    description = serializers.CharField(allow_null=True)
