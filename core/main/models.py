from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

# Вопрос
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    QUESTION_TYPES = (
        ('one', 'Один ответ'),
        ('multiple', 'Несколько ответов'),
        ('true_false', 'Правда/Ложь'),
    )
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)

# Вариант ответа к вопросу
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

# Сессия тестирования
class TestLaunch(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    classrooms = models.ManyToManyField(Classroom, blank=True)
    launched_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.launched_at:
            self.launched_at = timezone.now()

        # Если expires_at не указано, не меняем флаг, если пользователь сам задал is_active
        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False
        elif self.expires_at and not self._manual_is_active_override:
            self.is_active = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test.title} – {self.session_id}"

# Ответ ученика
class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_launch = models.ForeignKey(TestLaunch, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)
    is_checked = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

# Результат прохождения теста
class StudentTestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_launch = models.ForeignKey(TestLaunch, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'test_launch')


