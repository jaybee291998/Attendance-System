from rest_framework import permissions

class OwnerOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if self.user == obj.user:
			return True
		return False
		
class InstructorOnly(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.user.profile.role == 'I':
			return True
		return False

class InstructorOrAdministratorOnly(permissions.BasePermission):

	def has_permission(self, request, view):
		user_role = request.user.profile.role;
		if user_role == 'I' or user_role == 'A':
			return True
		return False;