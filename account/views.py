from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import CustomUserSerializer, UserProfileSerializer, YearLevelSerializer, SectionSerializer, PeriodSerializer, SubjectSerializer
from .permissions import OwnerOnly, InstructorOnly
from .models import YearLevel, Section, UserProfile, Period, Subject

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

class UserProfileDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, OwnerOnly]

    # def get_object(self, pk):
    #     try:
    #         user_profile = UserProfile.objects.get(pk=pk)
    #         return user_profile;
    #     except  UserProfile.DoesNotExist:
            # return None

    # def get(self, request, pk, format=None):
    #     user_profile = self.get_object(pk)
    #     if user_profile is not None:
    #         self.check_object_permissions()
    #         serializer = UserProfileSerializer(user_profile)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        user_profile = request.user.profile
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class YearLevelAndSectionList(APIView):
    def get(self, request, format=None):
        year_levels = YearLevel.objects.all()
        year_level_serializer = YearLevelSerializer(year_levels, many=True)
        sections = Section.objects.all()
        section_serializer = SectionSerializer(sections, many=True)
        context = {
            "year_levels": year_level_serializer.data,
            "sections": section_serializer.data
        }
        return Response(context
            , status=status.HTTP_200_OK)

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
        context['account_details'] = CustomUserSerializer(user).data
        context['profile'] = UserProfileSerializer(user.profile).data

        return Response(context, status=status.HTTP_200_OK)

    # it failed
    context['response'] = "Error"
    context['error_message'] = "invalid ceredentials"
    
    return Response(context, status=status.HTTP_401_UNAUTHORIZED)

class CreateUserWithProfile(APIView):
    def post(self, request, format=None):
        # print(request.data)
        serializer = CustomUserSerializer(data=request.data["user"])
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=request.data["user"]["email"])
            profile_serializer = UserProfileSerializer(user.profile, data=request.data["user_profile"])
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(profile_serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllRegisteredUserProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_role = request.user.profile.role
        if user_role == 'I' or user_role == 'A':
            user_profiles = UserProfile.objects.all()
            serializer = UserProfileSerializer(user_profiles, many=True, fields=('id', 'first_name', 'last_name', 'year_level', 'section', 'qr_code'))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            error = {
                "unauthorized" : "you must be an instructor or an admin to access this"
            }
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

class PeriodList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, InstructorOnly]

    def get(self, request, format=None):
        periods = request.user.periods.all();
        serializer = PeriodSerializer(periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PeriodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectList(APIView):
    def get(self, request, format=None):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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