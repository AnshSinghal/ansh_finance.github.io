import django_filters
from .models import FinancialRecord


class RecordFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name="type")
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = FinancialRecord
        fields = ["type", "category", "date_from", "date_to", "min_amount", "max_amount"]
