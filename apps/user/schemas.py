from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from .serializers import ProfileSerializer
from .serializers import UpdateProfileSerializer
from .serializers import LogoutSerializer

register_schema = extend_schema(
    tags=["User"],
    summary="User Registration",
    description="""
Register a new user (Customer or Provider) with nested profiles.

Available Roles:
- customer (requires 'customer' nested data)
- provider (requires 'provider' nested data)

Admin users cannot register through this API.
""",
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
    },
)

login_schema = extend_schema(
    tags=["User"],
    summary="User Login",
    description="""
Login with email and password.
Returns access and refresh tokens.
""",
    request=LoginSerializer,
    responses={
        200: LoginSerializer,
    },
)

profile_schema = extend_schema(
    tags=["User"],
    summary="User Profile",
    description="""
Get user profile.
""",
    responses={
        200: ProfileSerializer,
    },
)
update_profile_schema = extend_schema(
    tags=["User"],
    summary="Update Profile",
    description="Update logged-in user's profile.",
    request=UpdateProfileSerializer,
    responses={200: UpdateProfileSerializer},
)

logout_schema = extend_schema(
    tags=["User"],
    summary="Logout",
    description="Blacklist Refresh Token.",
    request=LogoutSerializer,
)