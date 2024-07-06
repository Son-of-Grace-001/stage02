from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from .serializers import CustomUserSerializer, OrganisationSerializer
from .models import CustomUser, Organisation
from django.contrib.auth import get_user_model
User = get_user_model()
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


logger = logging.getLogger(__name__)

class UserRegistration(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            User = serializer.save()
            # Create a default organisation
            org_name = f"{User.firstName}'s Organisation"
            Organisation.objects.create(name=org_name, created_by=User).users.add(User)
            refresh = RefreshToken.for_user(User)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": {
                        "userId": str(User.userId),
                        "firstName": User.firstName,
                        "lastName": User.lastName,
                        "email": User.email,
                        "phone": User.phone,
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "errors": [{"field": k, "message": v[0]} for k, v in serializer.errors.items()]
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserLogin(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        email = request.data.get('email')
        print (email)
        password = request.data.get('password')
        print (password)
        User = authenticate(password=password, email=email)
        if User is not None:
            login(request, User)
            refresh = RefreshToken.for_user(User)
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": {
                        "userId": str(User.userId),
                        "firstName": User.firstName,
                        "lastName": User.lastName,
                        "email": User.email,
                        "phone": User.phone,
                    }
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(userId=id)
            if user == request.user or request.user.organisations.filter(users__userId=id).exists():
                serializer = CustomUserSerializer(user)
                return Response({
                    "status": "success",
                    "message": "User details retrieved successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Unauthorized",
                "message": "You do not have permission to view this user's details",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return Response({
                "status": "Not found",
                "message": "User not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

class OrganisationList(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all() | request.user.created_organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {"organisations": serializer.data}
        }, status=status.HTTP_200_OK)

class OrganisationDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orgId):
        try:
            organisation = Organisation.objects.get(orgId=orgId)
            if request.user in organisation.users.all() or organisation.created_by == request.user:
                serializer = OrganisationSerializer(organisation)
                return Response({
                    "status": "success",
                    "message": "Organisation details retrieved successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Unauthorized",
                "message": "You do not have permission to view this organisation's details",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Not found",
                "message": "Organisation not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

class CreateOrganisation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save(created_by=request.user)
            organisation.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "errors": [{"field": k, "message": v[0]} for k, v in serializer.errors.items()]
        }, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        try:
            organisation = Organisation.objects.get(orgId=orgId)
            if organisation.created_by == request.user:
                userId = request.data.get('userId')
                try:
                    user = CustomUser.objects.get(userId=userId)
                    organisation.users.add(user)
                    return Response({
                        "status": "success",
                        "message": "User added to organisation successfully",
                    }, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    return Response({
                        "status": "Not found",
                        "message": "User not found",
                        "statusCode": 404
                    }, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "status": "Unauthorized",
                "message": "You do not have permission to add users to this organisation",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Not found",
                "message": "Organisation not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)