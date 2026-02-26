from rest_framework.views import APIView # Base class for API endpoints
from rest_framework.response import Response # To send JSON responses
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework import status # HTTP status codes (200, 400, 401, etc.)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model # To reference CustomUser
from rest_framework.permissions import IsAuthenticated # Protect endpoints

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from django.middleware.csrf import get_token

from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import LoginSerializer, RegisterSerializer, MeSerializer
from rest_framework.authentication import SessionAuthentication

User = get_user_model() # Get the CustomUser model

class LoginUserAPIView(APIView):

    """
    API endpoint for user login.

    Request:
        - email (string): User's email address
        - password (string): User's password

    Responses:
        - 200 OK: Credentials are correct; login successful
        - 400 Bad Request: Required fields missing
        - 401 Unauthorized: Invalid credentials

    Authentication is handled via session cookies with expiration.
    """

    authentication_classes = []
    permission_classes = []

    @extend_schema(
            request=LoginSerializer,
            responses={
                200: OpenApiResponse(
                    description="Login successful",
                    response={"message": "Login successful"},
                ),
                400: OpenApiResponse(
                    description="Email or password not provided",
                    response={"error": "Email and password are required."},
                ),
                401: OpenApiResponse(
                    description="Invalid credentials",
                    response={"error": "Invalid credentials"},
                ),
            },
    )

    def post(self, request):
        """
        Handle POST request to log in a user.

        Args:
            request (Request): The HTTP request containing 'email' and 'password'

        Returns:
            Response: JSON response with success message or error message.
        """

        # Extract credentials from request and convert email to lowercase
        email = request.data.get("email", "").lower()
        password = request.data.get("password")

        # Validate that both fields are provided
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Authenticate user using Django
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user) # Create session cookie
            request.session.set_expiry(86400) # Session expires in 24 hours
            return Response(
                {"message": "Login successful"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutUserAPIView(APIView):
    """
    API endpoint for logging out the authenticated user.

    Requires the user to be logged in. Deletes the active session cookie.

    Responses:
        - 200 OK: Logged out successfully
        - 401 Unauthorized: User not authenticated
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Logout successful",
                response={"message": "Logged out successfully"},
            ),
            401: OpenApiResponse(
                description="User not authenticated",
            ),
        }
    )

    @method_decorator(csrf_exempt) # 👈 Permite logout sin chequear CSRF
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """
        Handle POST request to log out a user.

        Args:
            request (Request): The HTTP request from an authenticated user

        Returns:
            Response: JSON response with logout confirmation.
        """
        logout(request) # Django clears the session automatically
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid', path='/')
        response.delete_cookie('csrftoken', path='/')
        return response

class RegisterUserAPIView(APIView):
    """
    API endpoint for registering a new user.

    The user is automatically assigned to the default team ("Default").
    Sending the 'team' field in the request is not allowed.

    Request:
        - email (string): User email
        - password (string): User password

    Responses:
        - 201 Created: User created successfully
        - 400 Bad Request: Invalid data or email already exists
    """

    authentication_classes = [BasicAuthentication]  # no requiere CSRF
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User created successfully",
                response={
                    "id": 1,
                    "email": "user@email.com",
                    "team": "Default",
                },
            ),
            400: OpenApiResponse(
                description="Invalid data or email already exists",
                response={"error": "Email already registered."},
            ),
        },
    )
    

    def post(self, request):
        """
        Handle POST request to register a new user.

        Args:
            request (Request): The HTTP request containing 'email' and 'password'

        Returns:
            Response: JSON response with created user info or error message.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Llama a create() del serializer y valida password
            return Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "team": user.team.name if user.team else None,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class MeAPIView(APIView):
#     """
#     Returns the currently authenticated user.
#     """

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         responses={
#             200: MeSerializer,
#             401: OpenApiResponse(
#                 description="Authentication required",
#             ),
#         }
#     )

#     # @method_decorator(ensure_csrf_cookie) # 👈 ESTA ES LA CLAVE: envía el token al cargar
#     # def dispatch(self, *args, **kwargs):
#     #     return super().dispatch(*args, **kwargs)

#     # def get(self, request):
#     #     serializer = MeSerializer(request.user)
#     #     return Response(serializer.data, status=status.HTTP_200_OK)
# class MeAPIView(APIView):
#     """
#     Returns the currently authenticated user.
#     """
#     # 1. Quitamos la autenticación de sesión de DRF para esta vista
#     # Esto evita el error 403 por CSRF para usuarios anónimos.
#     authentication_classes = [] 
#     permission_classes = [AllowAny]

#     @extend_schema(
#         responses={
#             200: MeSerializer,
#             401: OpenApiResponse(description="Authentication required"),
#         }
#     )
#     def get(self, request):
#         # 2. El middleware de Django ya identificó al usuario, así que validamos:
#         if request.user.is_authenticated:
#             # 3. Solo generamos el token si el usuario es real
#             get_token(request) 
#             serializer = MeSerializer(request.user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#         # 4. Si es anónimo, devolvemos 401 limpio (sin cookies de CSRF)
#         return Response(
#             {"detail": "Authentication credentials were not provided."}, 
#             status=status.HTTP_401_UNAUTHORIZED
#         )
    













class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # No hace nada, ¡así de simple!

class MeAPIView(APIView):
    # 1. Usamos nuestra clase especial que permite ver la sesión sin CSRF
    authentication_classes = [UnsafeSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 2. Si llegamos aquí, es porque UnsafeSession detectó al usuario
        # Ahora sí, generamos el token para que el usuario logueado lo tenga
        get_token(request) 
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class CSRFDebugMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
        
#         # Esto imprimirá en la consola CADA vez que algo intente poner una cookie
#         if response.cookies:
#             print(f"\n>>> COOKIES DETECTADAS EN: {request.path}")
#             for key, cookie in response.cookies.items():
#                 print(f"    - Nombre: {key}")
#                 if key == 'csrftoken':
#                     print("    !!!! ESTA ES LA QUE QUEREMOS QUITAR PARA ANÓNIMOS !!!!")
        
#         return response