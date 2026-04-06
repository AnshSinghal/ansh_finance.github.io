from decimal import Decimal
from django.db.models import Sum, Count, Case, When, DecimalField
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdmin, IsAnalystOrAdmin, IsAnyRole
from .filters import RecordFilter
from .models import FinancialRecord, RecordType
from .serializers import (
    RecordCreateSerializer,
    RecordResponseSerializer,
    RecordUpdateSerializer,
    SummarySerializer,
    CategoryBreakdownSerializer,
    TrendPointSerializer,
    RecentActivitySerializer,
)


class RecordListCreateView(generics.ListCreateAPIView):
    filter_class = RecordFilter
    search_fields = ["description", "category"]
    ordering_fields = ["date", "amount", "created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAnyRole()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecordCreateSerializer
        return RecordResponseSerializer

    def get_queryset(self):
        return FinancialRecord.objects.filter(deleted_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnyRole()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return RecordUpdateSerializer
        return RecordResponseSerializer

    def get_queryset(self):
        return FinancialRecord.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        record.deleted_at = timezone.now()
        record.save()
        return Response({"detail": "Record deleted."}, status=status.HTTP_200_OK)


class DashboardSummaryView(APIView):
    permission_classes = [IsAnyRole]

    def get(self, request):
        qs = FinancialRecord.objects.filter(deleted_at__isnull=True)
        agg = qs.aggregate(
            total_income=Sum(
                Case(When(type=RecordType.INCOME, then="amount"), default=0, output_field=DecimalField())
            ),
            total_expenses=Sum(
                Case(When(type=RecordType.EXPENSE, then="amount"), default=0, output_field=DecimalField())
            ),
            total_records=Count("id"),
        )
        income = agg["total_income"] or Decimal("0")
        expenses = agg["total_expenses"] or Decimal("0")
        data = {
            "total_income": income,
            "total_expenses": expenses,
            "net_balance": income - expenses,
            "total_records": agg["total_records"],
        }
        return Response(SummarySerializer(data).data)


class DashboardCategoriesView(APIView):
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        qs = FinancialRecord.objects.filter(deleted_at__isnull=True)
        income_rows = (
            qs.filter(type=RecordType.INCOME)
            .values("category")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        expense_rows = (
            qs.filter(type=RecordType.EXPENSE)
            .values("category")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        return Response({
            "income": CategoryBreakdownSerializer(income_rows, many=True).data,
            "expenses": CategoryBreakdownSerializer(expense_rows, many=True).data,
        })


class DashboardTrendsView(APIView):
    permission_classes = [IsAnalystOrAdmin]

    def get(self, request):
        granularity = request.query_params.get("granularity", "monthly")
        trunc_map = {"daily": TruncDay, "weekly": TruncWeek, "monthly": TruncMonth}
        Trunc = trunc_map.get(granularity, TruncMonth)

        qs = FinancialRecord.objects.filter(deleted_at__isnull=True)
        rows = (
            qs.annotate(period=Trunc("date"))
            .values("period")
            .annotate(
                income=Sum(
                    Case(When(type=RecordType.INCOME, then="amount"), default=0, output_field=DecimalField())
                ),
                expenses=Sum(
                    Case(When(type=RecordType.EXPENSE, then="amount"), default=0, output_field=DecimalField())
                ),
            )
            .order_by("period")
        )
        trends = [
            {
                "period": str(row["period"])[:10],
                "income": row["income"] or Decimal("0"),
                "expenses": row["expenses"] or Decimal("0"),
                "net": (row["income"] or Decimal("0")) - (row["expenses"] or Decimal("0")),
            }
            for row in rows
        ]
        return Response({"trends": TrendPointSerializer(trends, many=True).data, "granularity": granularity})


class DashboardRecentView(APIView):
    permission_classes = [IsAnyRole]

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 10)), 50)
        records = FinancialRecord.objects.filter(deleted_at__isnull=True).order_by("-date", "-created_at")[:limit]
        return Response({"recent": RecentActivitySerializer(records, many=True).data})
