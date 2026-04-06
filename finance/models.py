import uuid
from django.db import models
from django.conf import settings


class RecordType(models.TextChoices):
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="records"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    type = models.CharField(max_length=10, choices=RecordType.choices)
    category = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]

    @property
    def is_deleted(self):
        return self.deleted_at is not None
