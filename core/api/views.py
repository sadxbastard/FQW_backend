from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .serializers import RegisterSerializer, ClassroomSerializer, TestSerializer, StudentSerializer
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

# Создание тестов
class TestCreateView(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        classroom = serializer.validated_data['classroom']
        if classroom.owner != self.request.user:
            raise PermissionDenied("Вы не можете создавать тесты в чужом классе.")
        serializer.save(created_by=self.request.user)

# Получение всех тестов
class UserTestsListView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    # Получение всех студентов определенного класса текущего пользователя
    def get_queryset(self):
        classroom_id = self.kwargs['classroom_id']
        # Проверяем, что пользователь — владелец этого класса
        return Student.objects.filter(classroom__id=classroom_id, classroom__owner=self.request.user)