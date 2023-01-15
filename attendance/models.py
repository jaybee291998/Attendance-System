from django.db import models

# Create your models here.

from account.models import CustomUser, Subject, Section, UserProfile, Period

class AttendanceRecord(models.Model):
	user_profile 		= models.ForeignKey(UserProfile, related_name="attendance_records", on_delete=models.CASCADE, null=True)
	period 				= models.ForeignKey(Period, related_name="attendance_records", on_delete=models.CASCADE, null=True)
	timestamp			= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.user_profile} {self.period} {self.timestamp.date()}'