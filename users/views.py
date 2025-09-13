from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .models import User, PendingUser
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta
import random
import string
from django.conf import settings
from django.contrib.auth.hashers import make_password

def send_verification_email(user):
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    user.verification_code = verification_code
    user.code_expiration = now() + timedelta(minutes=5)
    user.save()

    subject = "Your verification code"
    message = f"Your verification code is: {verification_code}\nPlease enter it within 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if pending_user.created_at + timedelta(minutes=5) > now():
            return Response({"message": "The verification code has been sent recently, please try later."}, status=status.HTTP_400_BAD_REQUEST)

        send_verification_email(pending_user)
        return Response({"message": "The verification code has been sent again. Please check your email."}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if not pending_user.is_code_valid(code):
            return Response({"message": "The verification code is not valid or expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password,
            is_staff=pending_user.is_staff
        )
        user.is_active = True
        user.is_client = pending_user.is_client
        user.save()
        pending_user.delete()

        return Response({"message": "The account was successfully activated."}, status=status.HTTP_200_OK)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if len(new_password) < 8:
            return Response(
                {"message": "The password should be 8 characters or more."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.code_expiration = now() + timedelta(minutes=5)
        user.temp_password = make_password(new_password)
        user.save()

        subject = "Password reset"
        message = f"The verification code: {verification_code}\nPlease enter it within 5 minutes."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "Verification code has been sent."}, status=status.HTTP_200_OK)


class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "This email is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if user.verification_code != code or user.code_expiration < now():
            return Response({"message": "The verification code is not valid or expired."}, status=status.HTTP_400_BAD_REQUEST)

        if user.temp_password:
            user.password = user.temp_password
            user.temp_password = None
            user.verification_code = None
            user.code_expiration = None
            user.save()
            return Response({"message": "The password has been successfully updated."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "There is no new password."}, status=status.HTTP_400_BAD_REQUEST)

# Admin API
class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if len(data['password']) < 8:
            return Response(
                {"message": "The password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "This email is already registered. Please log in."}, status=status.HTTP_400_BAD_REQUEST)
        # Search for an existing record with the same email
        pending_user, created = PendingUser.objects.get_or_create(
            email=data['email'],
            defaults={
                'username': data['username'],
                'password': data['password'], # Make sure the password is hashed
                'is_staff': True
            }
        )

        if not created:
            # If a new record was not created, check if the old record has expired
            if pending_user.created_at + timedelta(minutes=5) > now():
                return Response({"message": "Please wait until the previous attempt expires."}, status=status.HTTP_400_BAD_REQUEST)
            # Update the old record
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "A verification code has been sent to your email. Please confirm your email within 5 minutes."}, status=status.HTTP_200_OK)


class AdminLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            if user.is_client:
                return Response({"error": "Clients are not allowed to log in from this link"}, status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class AdminLogoutView(APIView):
    def post(self, request):
        try:
            # Delete the token associated with the user
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token or already logged out"}, status=status.HTTP_400_BAD_REQUEST)

# Client API
class ClientRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        data = request.data

        if len(data['password']) < 8:
            return Response(
                {"message": "The password must be 8 characters or more."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        pending_user, created = PendingUser.objects.get_or_create(
            email=data['email'],
            defaults={
                'username': data['username'],
                'password': data['password'],
                'is_client': True
            }
        )

        if not created:
            if pending_user.created_at + timedelta(minutes=5) > now():
                return Response({"message": "Please wait until the previous attempt expires."}, status=status.HTTP_400_BAD_REQUEST)
            pending_user.username = data['username']
            pending_user.password = data['password']
            pending_user.created_at = now()
            pending_user.save()

        send_verification_email(pending_user)
        return Response({"message": "A verification code has been sent. Please enter it within 5 minutes."}, status=status.HTTP_200_OK)


class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_client:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials or not a client"}, status=status.HTTP_401_UNAUTHORIZED)

class ClientLogoutView(APIView):
    def post(self, request):
        try:
            if request.user.is_client:
                token = Token.objects.get(user=request.user)
                token.delete()
                return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Not a client"}, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token or already logged out"}, status=status.HTTP_400_BAD_REQUEST)