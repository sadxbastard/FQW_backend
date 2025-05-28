from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from django.db.models import Q
from datetime import datetime

from .serializers import *
from main.models import *

# Регистрация
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Получение всех классов преподавателя / Создание класса
class ClassroomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Classroom.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Получение всех тестов преподавателя / Создание теста
class TestListCreateView(generics.ListCreateAPIView):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Получение информации о запущенных тестах / Запуск теста
class LaunchTestView(generics.ListCreateAPIView):
    serializer_class = TestLaunchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Получаем все запуски тестов, созданные в классах текущего пользователя.
        Поддерживает фильтрацию по classroom.
        """
        queryset = TestLaunch.objects.filter(
            classroom__owner=self.request.user
        ).select_related('test', 'classroom')

        classroom_id = self.request.query_params.get('classroom')
        if classroom_id:
            queryset = queryset.filter(classroom__id=classroom_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save()

# Получение / создание / редактирование вопросов и вариантов ответов к ним
### НЕОБХОДИМО ДОДЕЛАТЬ РЕДАКТИРОВАНИЕ - НЕ РАБОТАЕТ
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(test__created_by=self.request.user)

    def perform_create(self, serializer):
        test_id = self.kwargs.get('test_id')
        serializer.save(test_id=test_id)

# Получение всех студентов определенного класса текущего пользователя
class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs['classroom_id']
        # Проверяем, что пользователь — владелец этого класса
        return Student.objects.filter(classroom__id=classroom_id, classroom__owner=self.request.user)

# Добавление студента в класс
class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

# Отправка выбранных вариантов ответов на вопрос
class StudentAnswerView(generics.CreateAPIView):
    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer

# Получение информации (выбранных ответов) о прохождении теста учеником
class StudentTestAnswersView(generics.ListAPIView):
    serializer_class = StudentAnswerDetailSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        test_id = self.kwargs['test_id']
        return StudentAnswer.objects.filter(student__id=student_id, question__test__id=test_id)

# Автоматическая проверка и подсчет результатов прохождения теста студентом
class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student_id = request.data.get('student_id')
        test_id = request.data.get('test_id')

        if not student_id or not test_id:
            return Response({'error': 'student_id and test_id are required'}, status=400)

        answers = StudentAnswer.objects.filter(
            student_id=student_id,
            question__test_id=test_id
        ).select_related('question').prefetch_related('selected_answers')

        correct_count = 0
        total_checked = 0

        for answer in answers:
            if answer.question.question_type in ['one', 'multiple']:
                correct_ids = set(
                    answer.question.answers.filter(is_correct=True).values_list('id', flat=True)
                )
                selected_ids = set(answer.selected_answers.values_list('id', flat=True))

                is_correct = correct_ids == selected_ids
                answer.is_correct = is_correct
                answer.is_checked = True
                answer.save()

                total_checked += 1
                if is_correct:
                    correct_count += 1

        # Сохраняем результат
        score = (correct_count / total_checked) * 100 if total_checked else 0

        StudentTestResult.objects.update_or_create(
            student=Student.objects.get(id=student_id),
            test=Test.objects.get(id=test_id),
            defaults={
                'score': score,
                'completed_at': datetime.now()
            }
        )

        return Response({'message': 'Test submitted and checked', 'score': score}, status=200)

# Получение текстовых ответов по тесту
class TextAnswersByTestView(generics.ListAPIView):
    serializer_class = TextAnswerReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        test_id = self.kwargs['test_id']
        return StudentAnswer.objects.filter(
            question__test_id=test_id,
            question__question_type='text'
        ).select_related('student', 'question')

# Ручная проверка текстового ответа (обновление отметки ответа)
class MarkTextAnswerView(generics.UpdateAPIView):
    queryset = StudentAnswer.objects.filter(question__question_type='text')
    serializer_class = TextAnswerCheckSerializer
    permission_classes = [IsAuthenticated]

# Список результатов по классу
class ClassTestResultsView(generics.ListAPIView):
    serializer_class = StudentTestResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        class_id = self.kwargs['class_id']
        return StudentTestResult.objects.filter(
            student__classroom__id=class_id,
            student__classroom__owner=self.request.user
        ).select_related('test', 'student')

# Список результатов ученика (доступна, как для учителя, так и для ученика)
class StudentTestResultsView(generics.ListAPIView):
    serializer_class = StudentTestResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return StudentTestResult.objects.filter(
            student__id=student_id
        ).select_related('test', 'student')