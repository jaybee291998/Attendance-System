from django.contrib import admin

from .models import CustomUser, UserProfile, Subject, AcademicYear, YearLevel, Section, Period, InstructorshipRequest

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Subject)
admin.site.register(AcademicYear)
admin.site.register(YearLevel)
admin.site.register(Section)
admin.site.register(Period)
admin.site.register(InstructorshipRequest)
