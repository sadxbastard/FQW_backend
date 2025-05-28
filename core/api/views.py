from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .serializers import *
from main.models import *

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassroomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Classroom.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TestListCreateView(generics.ListCreateAPIView):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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

class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    # Получение всех студентов определенного класса текущего пользователя
    def get_queryset(self):
        classroom_id = self.kwargs['classroom_id']
        # Проверяем, что пользователь — владелец этого класса
        return Student.objects.filter(classroom__id=classroom_id, classroom__owner=self.request.user)

# Вью для добавления студента в класс
class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

# Вью для отправки ответа на вопрос
class StudentAnswerView(generics.CreateAPIView):
    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer