from rest_framework import serializers
from main.models import *

# Для регистрации
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
    # Валидация данных при регистрации
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

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'answers']

    # Валидация вопроса при его создании
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question

    # Валидация вопроса при его редактировании
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)

        instance.text = validated_data.get('text', instance.text)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.save()

        if answers_data is not None:
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)

        return instance

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
    selected_answers = serializers.PrimaryKeyRelatedField(
        queryset=Answer.objects.all(), many=True, required=False
    )

    class Meta:
        model = StudentAnswer
        fields = ['id', 'student', 'question', 'selected_answers', 'text_answer']

    def create(self, validated_data):
        selected_answers = validated_data.pop('selected_answers', [])
        student_answer = StudentAnswer.objects.create(**validated_data)
        student_answer.selected_answers.set(selected_answers)
        return student_answer

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']

class StudentAnswerDetailSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    selected_answer_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        source='selected_answers'
    )

    all_answers = AnswerOptionSerializer(source='question.answers', many=True, read_only=True)

    class Meta:
        model = StudentAnswer
        fields = [
            'id',
            'question_id',
            'question_text',
            'question_type',
            'all_answers',
            'selected_answer_ids',
            'text_answer',
            'is_checked',
            'is_correct',
        ]
# Для результатов прохождения тестов
class StudentTestResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title')
    student_name = serializers.CharField(source='student.name')

    class Meta:
        model = StudentTestResult
        fields = ['id', 'test_title', 'student_name', 'score', 'completed_at']