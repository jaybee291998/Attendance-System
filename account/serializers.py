from rest_framework import serializers
from .models import CustomUser, UserProfile, YearLevel, Section, Period, Subject, AcademicYear

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'date_joined', 'password']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def save(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        account = CustomUser.objects.create_user(email=email, password=password)
        return account

class UserProfileSerializer(DynamicFieldsModelSerializer):
    def validate(self, data):
        if data['year_level'] != data['section'].year_level:
            raise serializers.ValidationError({'section':'section must be in the year level'})
        return data
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['role', 'qr_code', 'user']

class YearLevelSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = YearLevel
        fields = '__all__'
        read_only_fields = ['name', 'num_equivalent']

class SectionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['name', 'year_level']

class SubjectSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ['name']

class PeriodSerializer(DynamicFieldsModelSerializer):

    def validate(self, data):
        section = data['section']
        subject = data['subject']
        latest_acad_year = AcademicYear.objects.latest('timestamp')
        same_period = Period.objects.filter(section=section).filter(subject=subject).filter(academic_year=latest_acad_year)
        if same_period.exists():
            raise serializers.ValidationError({
                'section': f'A period with the same section and subject already exists({latest_acad_year})',
                'first_instructor': f'This instructor "{same_period[:1].get().instructor.profile}" has already registered this period'
                })
        return data;

    class Meta:
        model = Period
        fields = '__all__'
        read_only_fields = ['instructor', 'academic_year']