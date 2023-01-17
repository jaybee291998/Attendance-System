from django.urls import path

from . import views

urlpatterns = [
	path('attendance-records/<int:period_pk>/', views.AttendanceRecordList.as_view(), name='attendance_records'),
]