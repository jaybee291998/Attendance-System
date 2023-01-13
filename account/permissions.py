from rest_framework import permissions

class OwnerOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if self.user == obj.user:
			return True
		return False
		
class InstructorOnly(permissions.BasePermission):

	def has_permission(self, request, view):
		if self.user.profile.role == 'I':
			return True