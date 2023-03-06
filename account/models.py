import random, string

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from random_username.generate import generate_username

from .managers import CustomUserManager
# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class YearLevel(models.Model):
    name                = models.CharField(max_length=32)
    num_equivalent      = models.IntegerField()

    def __str__(self):
        return f'{self.name}'

class Section(models.Model):
    name                = models.CharField(max_length=32)
    year_level          = models.ForeignKey(YearLevel, related_name="sections", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.year_level.name} - {self.name}'

class UserProfile(models.Model):
    
    class SexChoices(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    class RoleChoices(models.TextChoices):
        STUDENT         = 'S', _('Student')
        INSTRUCTOR      = 'I', _('Teacher')
        ADMIN           = 'A', _('Head Teacher')

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )

    first_name          = models.CharField(max_length=32, null=True)
    last_name           = models.CharField(max_length=32, null=True)
    middle_name         = models.CharField(max_length=32, null=True)
    age                 = models.IntegerField(null=True)
    SexChoices          = models.CharField(
                            max_length=1,
                            choices=SexChoices.choices,
                            default=SexChoices.MALE,
                            null=True
                        )
    address             = models.CharField(max_length=1024, null=True)
    phone               = models.CharField(max_length=11, null=True)
    year_level          = models.ForeignKey(YearLevel, related_name="user_profiles", on_delete=models.CASCADE, null=True)
    section             = models.ForeignKey(Section, related_name="user_profiles", on_delete=models.CASCADE, null=True)
    role                = models.CharField(
                            max_length=1,
                            choices=RoleChoices.choices,
                            default=RoleChoices.STUDENT,
                            null=True
                        )
    qr_code             = models.CharField(max_length=16, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.user.email}'

class Subject(models.Model):
    name                = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'

class AcademicYear(models.Model):
    start_date          = models.DateField()
    end_date            = models.DateField()
    timestamp           = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'AY {self.start_date.year}-{self.end_date.year}'

class Period(models.Model):
    subject             = models.ForeignKey(Subject, related_name="periods", on_delete=models.CASCADE, null=True)
    section             = models.ForeignKey(Section, related_name="periods", on_delete=models.CASCADE, null=True)
    instructor          = models.ForeignKey(CustomUser, related_name="periods", on_delete=models.CASCADE, null=True)
    academic_year       = models.ForeignKey(AcademicYear, related_name="periods", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.section.year_level.name} {self.section.name} - {self.subject.name}'

class InstructorshipRequest(models.Model):

    class RoleChoices(models.TextChoices):
        INSTRUCTOR      = 'I', _('Teacher')
        ADMIN           = 'A', _('Head Teacher')

    class StatusChoices(models.TextChoices):
        PENDING         = 'P', _('Pending')
        ACCEPTED        = 'A', _('Accepted')
        REJECTED        = 'R', _('Rejected')

    requestee           = models.ForeignKey(CustomUser, related_name="my_instructorship_request", on_delete=models.CASCADE, null=True)
    role                = models.CharField(max_length=1, choices=RoleChoices.choices, default=RoleChoices.INSTRUCTOR, null=True)
    status              = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING, null=True)
    approvee            = models.ForeignKey(CustomUser, related_name="instructorship_request", on_delete=models.CASCADE, null=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requestee}({self.status})'

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        qr_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        UserProfile.objects.create(user=instance, qr_code=qr_code)

@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=CustomUser)
def generate_auth_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=Period)
def set_academic_year(sender, instance, created, **kwargs):
    if created:
        latest_acad_year = AcademicYear.objects.latest('timestamp')
        instance.academic_year = latest_acad_year
        instance.save()