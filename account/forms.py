from django import forms 
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class UserLoginForm(forms.Form):
	email = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'username', 'class':'form-control'}))
	password = password = forms.CharField(widget = forms.PasswordInput(attrs={'placeholder':'password', 'class':'form-control'}))

	def clean(self, *args, **kwargs):
		email = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')

		if not User.objects.filter(email=email).exists():
			raise forms.ValidationError(f'"{email}" does not exist')
		user = authenticate(email=email, password=password)
		if not user:
			raise forms.ValidationError("Invalid password")

		return super(UserLoginForm, self).clean(*args, **kwargs)
