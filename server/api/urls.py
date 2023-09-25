from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import ProfessorViewSet, StudentViewSet, CurrentUserView, StudentMarksView, ProfessorMarkGroups, \
    GroupMarksView

auth_router = routers.SimpleRouter()
auth_router.register('auth/users/professors', ProfessorViewSet, basename="professors")
auth_router.register('auth/users/students', StudentViewSet, basename="students")

jwt_urlpatterns = [
    path('jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

common_user_urlpatterns = [
    path('auth/users', CurrentUserView.as_view(), name='current_user')
]

marks_user_urlpatterns = [
    path('marks/<int:stud_id>', StudentMarksView.as_view(), name='student_marks'),
    path('marks/professor', ProfessorMarkGroups.as_view(), name='professor_markgroups'),
    path('marks/professor/<int:mark_group_id>', GroupMarksView.as_view(), name='professor_markgroups')
]

urlpatterns = []

urlpatterns += jwt_urlpatterns

urlpatterns += auth_router.urls

urlpatterns += common_user_urlpatterns

urlpatterns += marks_user_urlpatterns
