from django.urls import path
from .views import RegisterView, ClassroomListCreateView, TestCreateView, UserTestsListView, StudentListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    path('tests/create/', TestCreateView.as_view(), name='test-create'),
    path('tests/my/', UserTestsListView.as_view(), name='user-tests'),
    path('classrooms/<int:classroom_id>/students/', StudentListView.as_view(), name='student-list'),
]