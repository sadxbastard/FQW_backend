from rest_framework import serializers
from main.models import *

import uuid

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
        fields = ['id', 'name', 'student_count']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

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

# Сериализатор для списка тестов (только id и title)
class TestListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(
        source='questions.count',
        read_only=True
    )
    class Meta:
        model = Test
        fields = ['id', 'title', 'question_count']

# Сериализатор для детального теста (с вопросами и ответами)
class TestDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = Question.objects.create(test=test, **question_data)
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return test

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        questions_data = validated_data.get('questions')
        if questions_data is not None:
            existing_question_ids = {q.id for q in instance.questions.all()}
            incoming_question_ids = {q.get('id') for q in questions_data if 'id' in q}

            # Удаляем вопросы, которых больше нет в обновлённом списке
            to_delete = existing_question_ids - incoming_question_ids
            Question.objects.filter(id__in=to_delete).delete()

            for question_data in questions_data:
                answers_data = question_data.pop('answers', [])
                question_id = question_data.get('id')

                if question_id:
                    # Обновление существующего вопроса
                    question = Question.objects.get(id=question_id, test=instance)
                    question.text = question_data.get('text', question.text)
                    question.question_type = question_data.get('question_type', question.question_type)
                    question.save()

                    # Обновляем ответы
                    question.answers.all().delete()
                    for answer_data in answers_data:
                        Answer.objects.create(question=question, **answer_data)
                else:
                    # Создание нового вопроса
                    question = Question.objects.create(test=instance, **question_data)
                    for answer_data in answers_data:
                        Answer.objects.create(question=question, **answer_data)

        return instance

# class TestLaunchSerializer(serializers.ModelSerializer):
#     test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
#     classrooms = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Classroom.objects.all(),
#         required=False
#     )
#
#     class Meta:
#         model = TestLaunch
#         fields = [
#             'id', 'title', 'session_id', 'test', 'classrooms',
#             'launched_at', 'expires_at', 'is_active'
#         ]
#         read_only_fields = ['id', 'session_id']
#
#     def validate(self, data):
#         request = self.context['request']
#         instance = getattr(self, 'instance', None)
#
#         # Получаем test из данных или существующего экземпляра
#         test = data.get('test', None)
#         if test is None and instance:
#             test = instance.test
#
#         if test and test.created_by != request.user:
#             raise serializers.ValidationError("Вы не являетесь владельцем этого теста.")
#
#         # Для PATCH-запросов проверяем только переданные данные
#         classrooms = data.get('classrooms', None)
#
#         # Если classrooms/students не переданы в PATCH - пропускаем проверку
#         if self.partial and classrooms is None:
#             return data
#
#         # Для создания или явного обновления связей
#         if not self.partial or classrooms is not None:
#             classrooms = classrooms or []
#             for classroom in classrooms:
#                 if classroom.owner != request.user:
#                     raise serializers.ValidationError(f"Вы не владелец класса {classroom.name}.")
#
#         return data

# Сериализатор для работы со студентом

class TestLaunchSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    test_title = serializers.CharField(source='test.title', read_only=True)
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Classroom.objects.all(),
        required=False
    )
    is_scheduled = serializers.SerializerMethodField()

    class Meta:
        model = TestLaunch
        fields = [
            'id', 'title', 'session_id', 'test', 'classrooms',
            'launched_at', 'expires_at', 'is_active', 'is_scheduled', 'test_title'
        ]
        read_only_fields = ['id', 'session_id', 'is_scheduled']

    def get_is_scheduled(self, obj):
        return obj.is_scheduled

    def validate(self, data):
        request = self.context['request']
        instance = getattr(self, 'instance', None)

        test = data.get('test', None)
        if test is None and instance:
            test = instance.test

        if test and test.created_by != request.user:
            raise serializers.ValidationError("Вы не являетесь владельцем этого теста.")

        classrooms = data.get('classrooms', None)
        if self.partial and classrooms is None:
            return data

        if not self.partial or classrooms is not None:
            classrooms = classrooms or []
            for classroom in classrooms:
                if classroom.owner != request.user:
                    raise serializers.ValidationError(f"Вы не владелец класса {classroom.name}.")

        # Проверка, что expires_at не раньше launched_at
        launched_at = data.get('launched_at', getattr(instance, 'launched_at', None))
        expires_at = data.get('expires_at', None)

        if launched_at and expires_at and expires_at < launched_at:
            raise serializers.ValidationError("Время окончания не может быть раньше времени начала.")

        return data

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'student_id', 'classroom']
        read_only_fields = ['student_id', 'id']

    def validate_classroom(self, value):
        request = self.context.get('request')
        if value.owner != request.user:
            raise serializers.ValidationError("Вы не являетесь владельцем этого класса.")
        return value

    def create(self, validated_data):
        validated_data['student_id'] = self.generate_unique_id()
        return super().create(validated_data)

    def generate_unique_id(self):
        # Генерация уникального 12-символьного идентификатора
        return uuid.uuid4().hex[:12]

class AnswerItemSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    selected_answers = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all(), many=True, required=False)

class SubmitAnswersStudentSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    test_launch_id = serializers.CharField()
    answers = AnswerItemSerializer(many=True)

class StudentTestResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    classroom = serializers.IntegerField(source='student.classroom.id', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = StudentTestResult
        fields = ['id', 'student', 'student_id', 'student_name', 'classroom', 'score', 'completed_at']

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
            'is_checked',
            'is_correct',
        ]


# Сериализатор для ручной отметки ответа на текстовый вопрос
# class TextAnswerCheckSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentAnswer
#         fields = ['id', 'is_correct', 'is_checked']
#
#     def update(self, instance, validated_data):
#         instance.is_correct = validated_data['is_correct']
#         instance.is_checked = True
#         instance.save()
#         return instance

# Получение данных для генерации теста и их валидация
class TestGenerationRequestSerializer(serializers.Serializer):
    topic = serializers.CharField()
    type_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0),
    )

    def validate(self, data):
        total = sum(data['type_distribution'].values())

        allowed_keys = {'one', 'multiple', 'true_false'}
        unknown_keys = set(data['type_distribution'].keys()) - allowed_keys
        if unknown_keys:
            raise serializers.ValidationError(
                f"Недопустимые типы вопросов: {', '.join(unknown_keys)}"
            )

        return data
