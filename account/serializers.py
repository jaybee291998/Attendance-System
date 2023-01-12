from rest_framework import serializers
from .models import CustomUser

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