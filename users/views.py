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
