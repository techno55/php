from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db import models

from django.db import models

class Question(models.Model):
    PART_CHOICES = [
        ('1', 'Part 1'),
        ('2', 'Part 2'),
        ('3', 'Part 3'),
        ('4', 'Part 4'),
        ('5', 'Part 5'),
        ('6', 'Part 6'),
        ('7', 'Part 7'),
    ]

    part = models.CharField(max_length=1, choices=PART_CHOICES)
    text = models.TextField()
    audio_file = models.FileField(upload_to='questions_audio/', blank=True, null=True)  # Part 3, 4 用
    image_file = models.ImageField(upload_to='questions_images/', blank=True, null=True)  # Part 1 用

    def __str__(self):
        return f"Part {self.part} - {self.text[:50]}"
    
class Result(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
    user_answers = models.JSONField()  # ユーザーの回答を保存するフィールドを追加

    def __str__(self):
        return f"{self.user.username} - {self.score}"

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    level = models.CharField(max_length=20, default='beginner')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='questions_users',
        blank=True,
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='questions_users',
        blank=True,
        verbose_name='user permissions'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
class Question(models.Model):
    question_text = models.TextField()
    question_type = models.CharField(max_length=20)
    choices = models.JSONField(null=True, blank=True)
    answer = models.CharField(max_length=255)
    explanation = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LearningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
