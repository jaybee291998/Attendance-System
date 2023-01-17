from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from account.permissions import OwnerOnly, InstructorOnly, InstructorOrAdministratorOnly

from account.models import Period, CustomUser, UserProfile, AcademicYear
from account.serializers import UserProfileSerializer, AcademicYearSerializer
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer
from datetime import date, datetime, timedelta
# Create your views here.

class AttendanceRecordList(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [InstructorOrAdministratorOnly]

	def get_object(self, period_pk, user):
		try:
			period = Period.objects.get(pk=period_pk)
		except Period.DoesNotExist:
			return None
		if period.instructor == user or user.profile.role == 'A': return period

		return None

	def get(self, request, period_pk, format=None):
		period = self.get_object(period_pk, request.user)
		if period is not None:
			start_date_str = request.query_params.get('start_date')
			end_date_str = request.query_params.get('end_date')
			academic_year_id = request.query_params.get('academic_year_id')
			print(period)

			attendance_records = None
			if start_date_str is not None and end_date_str is not None:
				# parse start_date and end_date
				date_format = '%Y-%m-%d'
				try:
					start_date = datetime.strptime(start_date_str, date_format)
					end_date = datetime.strptime(end_date_str, date_format) + timedelta(days=1)
				except ValueError:
					return Response({'invalid_date_str': 'please provide a valid date str YYYY-mm-dd'})
				# print(f'start_date: {start_date}, end_date: {end_date}')
				attendance_records = period.attendance_records.all().filter(timestamp__range=[start_date, end_date])
			else:
				# if start_date and end date are not provided the just give todays record
				start_date = date.today()
				end_date = start_date + timedelta(days=1)
				# print(f'start_date: {start_date}, end_date: {end_date}')
				attendance_records = period.attendance_records.all().filter(timestamp__range=[start_date, end_date])
				# print(attendance_records)
			if academic_year_id is not None:
				try:
					academic_year = AcademicYear.objects.get(pk=academic_year_id)
					attendance_records.filter(period__academic_year=academic_year)
				except AcademicYear.DoesNotExist:
					return Response({'invalid_AY': 'invalid academic_year'}, status=status.HTTP_400_BAD_REQUEST)
			else:
				academic_year = AcademicYear.objects.latest('timestamp')
				attendance_records.filter(period__academic_year=academic_year)

			attendance_record_serializer = AttendanceRecordSerializer(attendance_records, many=True)
			students = UserProfile.objects.filter(section=period.section).filter(role='S')
			students_serializer = UserProfileSerializer(students, many=True)

			data = {
				'attendance_records': attendance_record_serializer.data,
				'students': students_serializer.data
			}
			return Response(data, status=status.HTTP_200_OK)

		context = {
			'error': 'period does not exists or you have no right to access this period'
		}
		return Response(context, status=status.HTTP_401_UNAUTHORIZED)

	def post(self, request, period_pk, format=None):
		period = self.get_object(period_pk, request.user)
		if period is None: return Response({'period': 'period does not exists or you have no right to access this period'}, status=status.HTTP_401_UNAUTHORIZED)
		if type(request.data) != list: return Response({'invalid_data': 'please provide a list of strings'}, status=status.HTTP_400_BAD_REQUEST)
		attendance_records = []
		invalid_records = []
		valid_records = []
		for qr_code in request.data:
			if type(qr_code) != str: continue
			student_profile = None

			try: student_profile = UserProfile.objects.get(qr_code=qr_code)
			except UserProfile.DoesNotExist: continue

			if student_profile.section != period.section:
				invalid_records.append(f'This student {student_profile} is not on this period')
				continue

			new_attendance_record = {'user_profile': student_profile.pk, 'period': period.pk}
			valid_records.append(f'{student_profile.first_name} {student_profile.middle_name[:1].upper()}. {student_profile.last_name}')
			attendance_records.append(new_attendance_record)
		if len(attendance_records) == 0:
			d = {
				'no_valid_qr': 'no valid qr code has been detected',
				'invalid_records': invalid_records
			} 
			return Response(d, status=status.HTTP_400_BAD_REQUEST)
		serializer = AttendanceRecordSerializer(data=attendance_records, many=True)
		if serializer.is_valid():
			serializer.save()
			d = {"success": serializer.data, "failed": invalid_records, "valid_records": valid_records}
			return Response(d, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


