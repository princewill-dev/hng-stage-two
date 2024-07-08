from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from .models import *
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

User = get_user_model()



# return a json hello message
class IndexView(APIView):
    def get(self, request):
        status_code = status.HTTP_200_OK
        message = "Connection was successful"

        return Response({"message": message}, status=status_code)
    

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create a default organization for the user
            org_name = f"{user.firstName}'s Organisation"
            organisation = Organisation.objects.create(
                name=org_name,
                created_by=user
            )
            organisation.members.add(user)
            
            refresh = RefreshToken.for_user(user)
            user_data = UserResponseSerializer(user).data
            
            # Include organization data in the response
            org_data = OrganisationSerializer(organisation).data
            
            response_data = {
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': user_data,
                    'organisation': org_data
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Collect and format the validation errors
        errors = []
        for field, messages in serializer.errors.items():
            for message in messages:
                errors.append({
                    "field": field,
                    "message": message
                })

        return Response({
            "errors": errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = User.objects.filter(email=email).first()
            
            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                user_data = UserResponseSerializer(user).data
                response_data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': str(refresh.access_token),
                        'user': user_data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Authentication failed',
                    'statusCode': 401,
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Collect and format the validation errors
        errors = []
        for field, messages in serializer.errors.items():
            for message in messages:
                errors.append({
                    "field": field,
                    "message": message
                })

        return Response({
            "errors": errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    

class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        try:
            user = User.objects.get(userId=userId)
            
            if request.user.userId != userId:
                return Response({
                    "status": "error",
                    "message": "You do not have permission to view this user's data"
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = UserResponseSerializer(user)
            data = {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone,
            }
            return Response({
                "status": "success",
                "message": "user data fetched successfully",
                "data": data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        

class OrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organisations = Organisation.objects.filter(
            Q(created_by=request.user) | 
            Q(members=request.user)
        ).distinct()
        
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Error creating organisation",
            "errors": [
                {"field": field, "message": message} 
                for field, messages in serializer.errors.items() 
                for message in messages
            ]
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY) 

class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Add this line

    def get_object(self, orgId):
        try:
            return Organisation.objects.get(orgId=orgId)
        except Organisation.DoesNotExist:
            raise Http404

    def get(self, request, orgId):
        try:
            organisation = self.get_object(orgId)
            serializer = OrganisationSerializer(organisation)
            return Response({
                "status": "success",
                "message": "Organisation retrieved successfully",
                "data": {
                    "orgId": serializer.data.get('orgId', ''),
                    "name": serializer.data.get('name', ''),
                    "description": serializer.data.get('description', ''),
                }
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        

class AddUserToOrganisationView(APIView):
    def post(self, request, orgId):
        userId = request.data.get('userId')
        if not userId:
            return Response({"message": "userId is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        organisation = get_object_or_404(Organisation, orgId=orgId)
        
        user = get_object_or_404(User, userId=userId)
        
        organisation.members.add(user)
        
        return Response({
            "status": "success",
            "message": "User added to organisation successfully"
        }, status=status.HTTP_200_OK)