from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
# GET/POST/PUT/DELETE
router.register(r'classrooms', ClassroomViewSet, basename='classroom')

router.register(r'students', StudentViewSet, basename='student') # GET: students/?classroom_id=number

router.register(r'tests', TestViewSet, basename='test')

router.register(r'test-launches', TestLaunchViewSet, basename='test-launch')


urlpatterns = [
    # POST | Зарегистрировать нового пользователя (преподавателя) по username и password
    path('register/', RegisterView.as_view(), name='register'),

    # POST | Аутентифицировать пользователя (получить access и refresh токены)
    path('login/', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # POST | Обновить access токен по текущему refresh токену
    path('token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),

    # -------------------------------------------------------------------------------------

    # POST | Отправить ответы на вопросы теста
    path('submit-answers/', SubmitAnswersStudentView.as_view(), name='submit-answer'),

    # PATCH | Ручная проверка текстового ответа (обновление отметки ответа)
    # path('text-answers/check/<int:pk>/', MarkTextAnswerView.as_view(), name='check-text-answer'),

    # GET | Получить результаты проведения тестирования по сессии
    path('results/<int:launch_id>/', TestLaunchResultView.as_view(), name='session-test-results'),

    ## GET | Получить тест, выбранные ответы и увидеть их состояние (проверено ли, правильность) по ученику и тесту
    path('student/<str:student_id>/launch/<int:launch_id>/answers/', StudentTestAnswersView.as_view(), name='student-test-answers'),

    # POST | Запрос на генерацию теста с указанием промпта
    path('generate-test/', GenerateTestView.as_view(), name='generate-test'),

    # POST | Запрос на экспорт теста в формат Word
    path('export/word/', ExportWordView.as_view(), name='export-word'),

]

urlpatterns += router.urls

urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]