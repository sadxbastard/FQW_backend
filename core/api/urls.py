from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

question_router = DefaultRouter()
# GET/POST
question_router.register(r'tests/(?P<test_id>\d+)/questions', QuestionViewSet, basename='test-questions')

urlpatterns = [
    # POST
    path('register/', RegisterView.as_view(), name='register'),
    # POST
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # POST
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # GET/POST
    path('tests/', TestListCreateView.as_view(), name='test-list-create'),
    # GET/POST
    path('tests/launch/', LaunchTestView.as_view(), name='test-launch'),
    # GET/POST
    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    # GET
    path('classrooms/<int:classroom_id>/students/', StudentListView.as_view(), name='student-list'),
    # POST
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    # POST
    path('submit-answer/', StudentAnswerView.as_view(), name='submit-answer'),
    # GET
    path('student-answers/<int:student_id>/<int:test_id>/', StudentTestAnswersView.as_view(), name='student-test-answers'),
    # POST
    path('submit-test/', SubmitTestView.as_view(), name='submit-test'),
    # GET
    path('results/class/<int:class_id>/', ClassTestResultsView.as_view(), name='class-test-results'),
    # GET
    path('results/student/<str:student_id>/', StudentTestResultsView.as_view(), name='student-test-results'),
    # GET
    path('text-answers/<int:test_id>/', TextAnswersByTestView.as_view(), name='text-answers-by-test'),
    # PATCH
    path('text-answers/check/<int:pk>/', MarkTextAnswerView.as_view(), name='check-text-answer'),
]

urlpatterns += question_router.urls

# Swagger

urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]