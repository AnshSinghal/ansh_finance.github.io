"""Run this once to write all Django project files."""
import pathlib, os

ROOT = pathlib.Path(__file__).parent


def w(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"  wrote {path}")


# ── config/settings.py ────────────────────────────────────────────────────────
w("config/settings.py", """\
from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-this-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "users",
    "finance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / os.environ.get("DB_NAME", "finance.db"),
    }
}

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/minute",
        "user": "300/minute",
        "auth": "10/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Finance API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin123!")
""")

# ── config/urls.py ─────────────────────────────────────────────────────────────
w("config/urls.py", """\
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/users/", include("users.user_urls")),
    path("api/v1/records/", include("finance.record_urls")),
    path("api/v1/dashboard/", include("finance.dashboard_urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
""")

# ── config/wsgi.py ─────────────────────────────────────────────────────────────
w("config/wsgi.py", """\
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
""")

# ── config/asgi.py ─────────────────────────────────────────────────────────────
w("config/asgi.py", """\
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
""")

# ── users/models.py ────────────────────────────────────────────────────────────
w("users/models.py", """\
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra):
        extra.setdefault("role", Role.ADMIN)
        extra.setdefault("is_staff", True)
        return self.create_user(username, email, password, **extra)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    @property
    def is_deleted(self):
        return self.deleted_at is not None
""")

# ── users/serializers.py ───────────────────────────────────────────────────────
w("users/serializers.py", """\
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

    def validate_username(self, value):
        if value and not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username must contain only alphanumeric characters and underscores."
            )
        return value

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
""")

# ── users/permissions.py ───────────────────────────────────────────────────────
w("users/permissions.py", """\
from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)


class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ANALYST, Role.ADMIN)
        )


class IsAnyRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
""")

# ── users/throttles.py ─────────────────────────────────────────────────────────
w("users/throttles.py", """\
from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    scope = "auth"
""")

# ── users/views.py ─────────────────────────────────────────────────────────────
w("users/views.py", """\
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .permissions import IsAdmin, IsAnyRole
from .serializers import (
    RegisterSerializer,
    UserResponseSerializer,
    UserRoleUpdateSerializer,
    UserUpdateSerializer,
)
from .throttles import AuthRateThrottle


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            user = User.objects.get(username=username, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "token_type": "bearer",
        })


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"detail": "Logged out."})
        except TokenError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserResponseSerializer
    permission_classes = [IsAnyRole]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = UserResponseSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = User.objects.filter(deleted_at__isnull=True).order_by("created_at")
        if not self.request.query_params.get("include_inactive") == "true":
            qs = qs.filter(is_active=True)
        return qs


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserResponseSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if str(user.pk) == str(request.user.pk):
            return Response({"detail": "Cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)
        user.deleted_at = timezone.now()
        user.is_active = False
        user.save()
        return Response({"detail": "User deleted."}, status=status.HTTP_200_OK)


class UserRoleUpdateView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.role = serializer.validated_data["role"]
        user.save()
        return Response(UserResponseSerializer(user).data)
""")

# ── users/urls.py ─────────────────────────────────────────────────────────────
w("users/urls.py", """\
from django.urls import path
from .views import RegisterView, LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
""")

# ── users/user_urls.py ─────────────────────────────────────────────────────────
w("users/user_urls.py", """\
from django.urls import path
from .views import MeView, UserListView, UserDetailView, UserRoleUpdateView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("me/", MeView.as_view(), name="user-me"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<uuid:pk>/role/", UserRoleUpdateView.as_view(), name="user-role"),
]
""")

# ── users/apps.py ─────────────────────────────────────────────────────────────
w("users/apps.py", """\
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.conf import settings as s
        from django.db.models.signals import post_migrate
        post_migrate.connect(_seed_admin, sender=self)


def _seed_admin(sender, **kwargs):
    from django.conf import settings as s
    from users.models import User, Role
    if not User.objects.filter(deleted_at__isnull=True).exists():
        User.objects.create_user(
            username=s.ADMIN_USERNAME,
            email=s.ADMIN_EMAIL,
            password=s.ADMIN_PASSWORD,
            first_name="Admin",
            last_name="User",
            role=Role.ADMIN,
        )
""")

# ── finance/models.py ─────────────────────────────────────────────────────────
w("finance/models.py", """\
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
""")

# ── finance/serializers.py ────────────────────────────────────────────────────
w("finance/serializers.py", """\
from rest_framework import serializers
from .models import FinancialRecord, RecordType


class RecordCreateSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)

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
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0.01, required=False)

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
""")

# ── finance/filters.py ────────────────────────────────────────────────────────
w("finance/filters.py", """\
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
""")

# ── finance/views.py ──────────────────────────────────────────────────────────
w("finance/views.py", """\
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
""")

# ── finance/record_urls.py ────────────────────────────────────────────────────
w("finance/record_urls.py", """\
from django.urls import path
from .views import RecordListCreateView, RecordDetailView

urlpatterns = [
    path("", RecordListCreateView.as_view(), name="record-list"),
    path("<uuid:pk>/", RecordDetailView.as_view(), name="record-detail"),
]
""")

# ── finance/dashboard_urls.py ─────────────────────────────────────────────────
w("finance/dashboard_urls.py", """\
from django.urls import path
from .views import DashboardSummaryView, DashboardCategoriesView, DashboardTrendsView, DashboardRecentView

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("categories/", DashboardCategoriesView.as_view(), name="dashboard-categories"),
    path("trends/", DashboardTrendsView.as_view(), name="dashboard-trends"),
    path("recent/", DashboardRecentView.as_view(), name="dashboard-recent"),
]
""")

# ── finance/apps.py ───────────────────────────────────────────────────────────
w("finance/apps.py", """\
from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finance"
""")

# ── tests/conftest / test files ───────────────────────────────────────────────
w("tests/__init__.py", "")

w("tests/test_auth.py", """\
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def register_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "viewer",
    }


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client, register_data):
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 201
        assert resp.data["username"] == "testuser"
        assert resp.data["role"] == "viewer"

    def test_register_duplicate_email(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        register_data["username"] = "other"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        register_data["email"] = "other@example.com"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_weak_password(self, client, register_data):
        register_data["password"] = "weak"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_invalid_email(self, client, register_data):
        register_data["email"] = "not-an-email"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        resp = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": register_data["password"]}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_wrong_password(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        resp = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": "Wrong123!"}, format="json")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login/", {"username": "nobody", "password": "Nobody123!"}, format="json")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestRefresh:
    def test_refresh_success(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        login = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": register_data["password"]}, format="json")
        resp = client.post("/api/v1/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_refresh_invalid_token(self, client):
        resp = client.post("/api/v1/auth/refresh/", {"refresh": "invalid"}, format="json")
        assert resp.status_code == 401
""")

w("tests/test_users.py", """\
import pytest
from rest_framework.test import APIClient
from users.models import User, Role


@pytest.fixture
def client():
    return APIClient()


def make_user(username, email, password, role="viewer"):
    return User.objects.create_user(username=username, email=email, password=password,
                                    first_name="F", last_name="L", role=role)


def auth(client, user, password):
    resp = client.post("/api/v1/auth/login/", {"username": user.username, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])


@pytest.mark.django_db
class TestListUsers:
    def test_admin_can_list_users(self, client):
        admin = make_user("adm", "adm@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 200

    def test_viewer_cannot_list_users(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 403

    def test_unauthenticated_cannot_list_users(self, client):
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestGetMe:
    def test_viewer_can_get_me(self, client):
        viewer = make_user("vw2", "vw2@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/users/me/")
        assert resp.status_code == 200
        assert resp.data["username"] == "vw2"


@pytest.mark.django_db
class TestUpdateRole:
    def test_admin_can_change_role(self, client):
        admin = make_user("adm2", "adm2@t.com", "Admin123!", role=Role.ADMIN)
        target = make_user("target", "target@t.com", "Target123!")
        auth(client, admin, "Admin123!")
        resp = client.patch(f"/api/v1/users/{target.pk}/role/", {"role": "analyst"}, format="json")
        assert resp.status_code == 200
        assert resp.data["role"] == "analyst"


@pytest.mark.django_db
class TestDeleteUser:
    def test_admin_can_soft_delete_user(self, client):
        admin = make_user("adm3", "adm3@t.com", "Admin123!", role=Role.ADMIN)
        target = make_user("del_target", "deltarget@t.com", "Target123!")
        auth(client, admin, "Admin123!")
        resp = client.delete(f"/api/v1/users/{target.pk}/")
        assert resp.status_code == 200
        target.refresh_from_db()
        assert target.deleted_at is not None

    def test_admin_cannot_delete_self(self, client):
        admin = make_user("adm4", "adm4@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.delete(f"/api/v1/users/{admin.pk}/")
        assert resp.status_code == 400
""")

w("tests/test_financial.py", """\
import pytest
from rest_framework.test import APIClient
from users.models import User, Role
from finance.models import FinancialRecord
import datetime


@pytest.fixture
def client():
    return APIClient()


def make_user(username, email, password, role="viewer"):
    return User.objects.create_user(username=username, email=email, password=password,
                                    first_name="F", last_name="L", role=role)


def auth(client, user, password):
    resp = client.post("/api/v1/auth/login/", {"username": user.username, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])


RECORD_DATA = {
    "amount": "150.00",
    "type": "income",
    "category": "Salary",
    "date": "2024-01-15",
    "description": "Monthly salary",
}


@pytest.mark.django_db
class TestCreateRecord:
    def test_admin_can_create_record(self, client):
        admin = make_user("adm", "adm@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.post("/api/v1/records/", RECORD_DATA, format="json")
        assert resp.status_code == 201
        assert resp.data["category"] == "Salary"

    def test_viewer_cannot_create_record(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.post("/api/v1/records/", RECORD_DATA, format="json")
        assert resp.status_code == 403

    def test_create_invalid_amount(self, client):
        admin = make_user("adm2", "adm2@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        data = {**RECORD_DATA, "amount": "-10"}
        resp = client.post("/api/v1/records/", data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestListRecords:
    def test_viewer_can_list_records(self, client):
        viewer = make_user("vw3", "vw3@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/records/")
        assert resp.status_code == 200

    def test_filter_by_type(self, client):
        admin = make_user("adm3", "adm3@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        client.post("/api/v1/records/", RECORD_DATA, format="json")
        resp = client.get("/api/v1/records/?type=income")
        assert resp.status_code == 200

    def test_search(self, client):
        admin = make_user("adm4", "adm4@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        client.post("/api/v1/records/", RECORD_DATA, format="json")
        resp = client.get("/api/v1/records/?search=Salary")
        assert resp.status_code == 200

    def test_pagination(self, client):
        viewer = make_user("vw4", "vw4@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/records/?page=1&page_size=5")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestUpdateRecord:
    def test_admin_can_update_record(self, client):
        admin = make_user("adm5", "adm5@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        resp = client.patch(f"/api/v1/records/{record_id}/", {"amount": "200.00"}, format="json")
        assert resp.status_code == 200

    def test_viewer_cannot_update_record(self, client):
        admin = make_user("adm6", "adm6@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        viewer = make_user("vw5", "vw5@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.patch(f"/api/v1/records/{record_id}/", {"amount": "200.00"}, format="json")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestDeleteRecord:
    def test_admin_can_soft_delete_record(self, client):
        admin = make_user("adm7", "adm7@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        resp = client.delete(f"/api/v1/records/{record_id}/")
        assert resp.status_code == 200
        record = FinancialRecord.objects.get(pk=record_id)
        assert record.deleted_at is not None

    def test_viewer_cannot_delete_record(self, client):
        admin = make_user("adm8", "adm8@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        viewer = make_user("vw6", "vw6@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.delete(f"/api/v1/records/{record_id}/")
        assert resp.status_code == 403
""")

w("tests/test_dashboard.py", """\
import pytest
from rest_framework.test import APIClient
from users.models import User, Role


@pytest.fixture
def client():
    return APIClient()


def make_user(username, email, password, role="viewer"):
    return User.objects.create_user(username=username, email=email, password=password,
                                    first_name="F", last_name="L", role=role)


def auth(client, user, password):
    resp = client.post("/api/v1/auth/login/", {"username": user.username, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])


RECORD_DATA = {"amount": "100.00", "type": "income", "category": "Salary", "date": "2024-01-01"}


@pytest.mark.django_db
class TestSummary:
    def test_viewer_can_access_summary(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 200
        assert "total_income" in resp.data

    def test_summary_empty(self, client):
        viewer = make_user("vw2", "vw2@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 200
        assert str(resp.data["total_income"]) == "0.00"

    def test_unauthenticated_cannot_access_summary(self, client):
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestCategories:
    def test_viewer_cannot_access_categories(self, client):
        viewer = make_user("vw3", "vw3@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/categories/")
        assert resp.status_code == 403

    def test_analyst_can_access_categories(self, client):
        analyst = make_user("an", "an@t.com", "Analyst123!", role=Role.ANALYST)
        auth(client, analyst, "Analyst123!")
        resp = client.get("/api/v1/dashboard/categories/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestTrends:
    def test_viewer_cannot_access_trends(self, client):
        viewer = make_user("vw4", "vw4@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/trends/")
        assert resp.status_code == 403

    def test_analyst_can_access_trends(self, client):
        analyst = make_user("an2", "an2@t.com", "Analyst123!", role=Role.ANALYST)
        auth(client, analyst, "Analyst123!")
        resp = client.get("/api/v1/dashboard/trends/")
        assert resp.status_code == 200
        assert "trends" in resp.data


@pytest.mark.django_db
class TestRecent:
    def test_viewer_can_access_recent(self, client):
        viewer = make_user("vw5", "vw5@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/recent/")
        assert resp.status_code == 200
        assert "recent" in resp.data
""")

# ── pytest.ini / pyproject.toml ───────────────────────────────────────────────
w("pyproject.toml", """\
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "finance-api"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "django>=4.2,<5.0",
    "djangorestframework>=3.15",
    "djangorestframework-simplejwt>=5.3",
    "django-filter>=24.0",
    "drf-spectacular>=0.27",
]

[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-django>=4.8",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
""")

# ── .env.example ──────────────────────────────────────────────────────────────
w(".env.example", """\
DJANGO_SECRET_KEY=change-this-in-production
DEBUG=True
ALLOWED_HOSTS=*
DB_NAME=finance.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_EMAIL=admin@example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin123!
""")

# ── .gitignore ────────────────────────────────────────────────────────────────
w(".gitignore", """\
.venv/
__pycache__/
*.pyc
*.pyo
*.db
*.db-shm
*.db-wal
.env
dist/
*.egg-info/
.pytest_cache/
""")

# ── Dockerfile ────────────────────────────────────────────────────────────────
w("Dockerfile", """\
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN python manage.py migrate --no-input

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
""")

# ── docker-compose.yml ────────────────────────────────────────────────────────
w("docker-compose.yml", """\
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-change-this-in-production}
      DEBUG: ${DEBUG:-False}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-*}
      ADMIN_EMAIL: ${ADMIN_EMAIL:-admin@example.com}
      ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD:-Admin123!}
    volumes:
      - ./finance.db:/app/finance.db
""")

print("All files written.")
