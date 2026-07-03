from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from .schemas import register_schema
from .serializers import LoginSerializer
from .schemas import login_schema
from .serializers import ProfileSerializer
from .schemas import profile_schema
from .serializers import UpdateProfileSerializer
from .schemas import update_profile_schema
from .serializers import LogoutSerializer
from .schemas import logout_schema


class RegisterAPIView(APIView):
    """
    User Registration API
    """

    serializer_class = RegisterSerializer

    permission_classes = (AllowAny,)

    @register_schema
    def post(self, request):

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    """
    User Login API
    """

    serializer_class = LoginSerializer

    permission_classes = (AllowAny,)

    @login_schema
    def post(self, request):

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": serializer.validated_data
            },
            status=status.HTTP_200_OK
        )

class ProfileAPIView(APIView):
    """
    User Profile API
    """

    serializer_class = ProfileSerializer

    permission_classes = (IsAuthenticated,)

    @profile_schema
    def get(self, request):

        serializer = self.serializer_class(
            request.user,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "message": "Profile fetched successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )  

class UpdateProfileAPIView(APIView):

    serializer_class = UpdateProfileSerializer

    permission_classes = (IsAuthenticated,)

    @update_profile_schema
    def patch(self, request):

        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        ) 

class LogoutAPIView(APIView):

    serializer_class = LogoutSerializer

    permission_classes = (IsAuthenticated,)

    @logout_schema
    def post(self, request):

        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )       
