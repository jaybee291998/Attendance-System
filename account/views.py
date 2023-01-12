from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import CustomUserSerializer

User = get_user_model()

class UserList(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', ])
def login(request):
    context = {}
    email = request.data.get('email')
    password = request.data.get('password')
    print(f'email: {email}')
    print(f'password: {password}')
    user = authenticate(email=email, password=password)
    if user:
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        context['response'] = "successfully authenticated"
        context['token'] = token.key
        context['account_details'] = CustomUserSerializer(user).data;
        return Response(context, status=status.HTTP_200_OK)

    # it failed
    context['response'] = "Error"
    context['error_message'] = "invalid ceredentials"
    
    return Response(context, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated])
def get_account_details(request):
    serializer = CustomUserSerializer(request.user);
    return Response(serializer.data);

@api_view(["POST", ])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated])
def secret(request):
    data = request.POST.get('data')
    return Response({'email': request.user.email, 'data': data})

@api_view(['POST', ])
def public(request):
    sensor = request.POST.get('sensor')
    return Response({'sensor': sensor})