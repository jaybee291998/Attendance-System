from django.urls import path
from . import views 

urlpatterns = [
    path('register/', views.UserList.as_view(), name="register"),
    path('login/', views.login, name="login"),
    path('secret/', views.secret, name="secret"),
    path('public/', views.public, name='public'),
    path('user-details/', views.get_account_details, name="account_details"),
    path('user-profile/', views.UserProfileDetail.as_view(), name="profile_detail"),
    path('year-section/', views.YearLevelAndSectionList.as_view(), name="year_level_and_section"),
    path('register-with-profile/', views.CreateUserWithProfile.as_view(), name="create_user_with_profile"),
    path('get-all-registered-user/', views.GetAllRegisteredUserProfile.as_view(), name="get_all_registered_user_profile"),
    path('subjects/', views.SubjectList.as_view(), name="subject_list"),
    path('period-list/', views.PeriodList.as_view(), name="period_list"),
    path('get-all-members/', views.GetAllMembers.as_view(), name='get_all_members'),
    path('request-instructorship-list/', views.RequestInstructorshipList.as_view(), name="request_instructorship_list"),
    path('request-instructorship-detail/<int:request_pk>/', views.RequestInstructorshipDetail.as_view(), name='request_instructorship_detail')
]
