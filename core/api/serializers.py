from rest_framework import serializers
from main.models import *

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'teacher')  # default: teacher
        )
        return user

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'owner']
        read_only_fields = ['id', 'owner']

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'description']

class TestLaunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestLaunch
        fields = ['id', 'test', 'classroom', 'launched_at', 'is_active']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name', 'student_id', 'classroom')

    def validate_classroom(self, value):
        request = self.context.get('request')
        if value.owner != request.user:
            raise serializers.ValidationError("Вы не являетесь владельцем этого класса.")
        return value

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'student', 'question', 'selected_answers', 'text_answer']