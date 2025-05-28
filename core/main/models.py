from django.contrib.auth.models import AbstractUser
from django.db import models

# Расширенный пользователь
class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')

# Класс
class Classroom(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')

# Ученик
class Student(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=12, unique=True)  # уникальный ID для прохождения тестов

# Тест
class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

# Сессия тестирования
class TestLaunch(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    launched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.test.title} → {self.classroom.name}"

# Вопрос
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    QUESTION_TYPES = (
        ('one', 'Один ответ'),
        ('multiple', 'Несколько ответов'),
        ('text', 'Развернутый ответ'),
    )
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)

# Варианты ответа
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

# Ответ ученика
class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)  # для one/multiple
    text_answer = models.TextField(blank=True)  # для text
    is_checked = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

# Результат прохождения теста
class StudentTestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)
