from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import CustomUserSerializer, UserProfileSerializer, YearLevelSerializer, SectionSerializer, PeriodSerializer, SubjectSerializer, InstructorshipRequestSerializer
from .permissions import OwnerOnly, InstructorOnly,InstructorOrAdministratorOnly, AdminOnly
from .models import YearLevel, Section, UserProfile, Period, Subject, InstructorshipRequest

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
        return Response(context, status=status.HTTP_200_OK)

class GetAllMembers(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AdminOnly]

    def get(self, request, format=None):
        role = request.query_params.get('role')
        if role is not None:
            if len(role) == 1:
                if role == 'I':
                    user_profiles = UserProfile.objects.filter(role='I')
                elif role == 'S':
                    user_profiles = UserProfile.objects.filter(role='S')
            else:
                user_profiles = UserProfile.objects.all()
        else:
            user_profiles = UserProfile.objects.all()

        serializer = UserProfileSerializer(user_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestInstructorshipList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_role = request.user.profile.role 
        if user_role == 'S':
            request = request.user.my_instructorship_request.all()
            serializer = InstructorshipRequestSerializer(request, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user_role == 'A':
            request_status = request.query_params.get('status')
            role = request.query_params.get('role')
            verified_status = None
            verified_role = None
            if request_status is not None:
                if(len(request_status) == 1):
                    if request_status == 'P': verified_status = 'P'
                    elif request_status == 'A': verified_status = 'A'
                    elif request_status == 'R': verified_status = 'R'
            if role is not None:
                if(len(role) == 1):
                    if role == 'I': verified_role = 'I'
                    elif role == 'A': verified_role = 'A'

            request = InstructorshipRequest.objects.all()
            if verified_status is not None: request = request.filter(status=verified_status)
            if verified_role is not None: request = request.filter(role=verified_role)
                # serializer = InstructorshipRequestSerializer(request, many=True)
                # return Response(serializer.data, status=status.HTTP_200_OK)

            
            serializer = InstructorshipRequestSerializer(request, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'unauthorized': 'only students and admin can access this resource'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        user_role = request.user.profile.role 
        if user_role == 'S':
            existing_request = request.user.my_instructorship_request.all().filter(status='P')
            if existing_request.exists(): return Response({'pending_request': 'you already have a pending request'}, status=status.HTTP_400_BAD_REQUEST)
            role = request.query_params.get('role')
            verified_role = 'I'
            if role is not None:
                if role == 'A':
                    verified_role = 'A'
            request = InstructorshipRequest.objects.create(requestee=request.user, role=verified_role)
            return Response({'pending_request': 'your request is now pending, please wait for approval or rejection'}, status=status.HTTP_200_OK)
        return Response({'request_instructorship': 'only students can request to be an instructor/head teacher'}, status=status.HTTP_401_UNAUTHORIZED)


class RequestInstructorshipDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AdminOnly]

    def get_object(self, request_pk):
        try:
            request = InstructorshipRequest.objects.get(pk=request_pk)
        except InstructorshipRequest.DoesNotExist:
            return None
        return request

    def put(self, request, request_pk, format=None):
        instructorship_request = self.get_object(request_pk)
        if instructorship_request is not None:
            if instructorship_request.status != 'P': return Response({'not_allowed': 'this request has already been processed, the status can no longer be changed'})
            request_status = request.query_params.get('status')
            if request_status is not None:
                if(len(request_status) == 1):
                    verified_status = None
                    # if request_status == 'P': verified_status = 'P'
                    if request_status == 'A': verified_status = 'A'
                    elif request_status == 'R': verified_status = 'R'

                    if verified_status is not None:
                        old_status = instructorship_request.status
                        instructorship_request.status = verified_status
                        instructorship_request.approvee = request.user
                        instructorship_request.save()
                        if verified_status == 'A':
                            requestee_profile = instructorship_request.requestee.profile
                            requestee_profile.role = instructorship_request.role
                            requestee_profile.save()
                        return Response({'request_updated': f'request status has been updated from {old_status} to {verified_status}'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'invalid_status': 'valid statuses are A, R'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'invalid_status':'a status is one char'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'no_status': 'please provide a status'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'invalid_instructorship_request': 'the instructorship_request is incvalid'}, status=status.HTTP_400_BAD_REQUEST)

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
            first_name = request.data["user_profile"]["first_name"].lower()
            last_name = request.data["user_profile"]["last_name"].lower()
            print(f'{first_name} {last_name}')
            existing_profile = UserProfile.objects.filter(first_name=first_name).filter(last_name=last_name)
            print(existing_profile)
            if existing_profile.exists(): return Response({'name_already_registered':f'The name "{first_name} {last_name}" is already is use by user_profile_id {existing_profile[:1].get().pk}'}, status=status.HTTP_400_BAD_REQUEST)
            custom_user = serializer.save()
            user = User.objects.get(email=request.data["user"]["email"])
            profile_serializer = UserProfileSerializer(user.profile, data=request.data["user_profile"])
            if profile_serializer.is_valid():
                role = request.query_params.get('role')
                verified_role = None
                if role is not None:
                    if role == 'A': verified_role = 'A'
                    elif role == 'I': verified_role = 'I'
                if verified_role is not None:
                    InstructorshipRequest.objects.create(requestee=custom_user, role=verified_role)
                profile_serializer.save()
                return Response(profile_serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(profile_serializer.error, status=HTTP_400_BAD_REQUEST)
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
    permission_classes = [IsAuthenticated, InstructorOrAdministratorOnly]

    def get_object(self, period_pk, user):
        try:
            period = Period.objects.get(pk=period_pk)
        except Period.DoesNotExist:
            return None

        if period.instructor == user: return period

        return None

    def get(self, request, format=None):
        user_role = request.user.profile.role;
        period_pk = request.query_params.get('period_pk')
        period = None
        if period_pk is not None: period = self.get_object(period_pk, request.user)

        if user_role == 'A':
            periods = Period.objects.all()
        elif period is not None:
            periods = Period.objects.filter(section=period.section)
        else:
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