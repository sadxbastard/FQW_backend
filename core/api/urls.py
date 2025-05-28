from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tests/', TestListCreateView.as_view(), name='test-list-create'),
    path('tests/launch/', LaunchTestView.as_view(), name='test-launch'),
    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    path('classrooms/<int:classroom_id>/students/', StudentListView.as_view(), name='student-list'),
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('answers/', StudentAnswerView.as_view(), name='submit-answer'),
    path('student-answers/<int:student_id>/<int:test_id>/', StudentTestAnswersView.as_view(), name='student-test-answers'),
]