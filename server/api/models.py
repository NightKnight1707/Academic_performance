from django.conf import settings
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from api.validators import CustomUnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractUser):
    username_validator = CustomUnicodeUsernameValidator()
    username = models.CharField(
        _('Логин'),
        max_length=50,
        unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('Имя'), max_length=20, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=20, blank=True)
    patronymic = models.CharField(_('Отчество'), max_length=20, blank=True)
    email = models.EmailField(
        _('Адрес электронной почты'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('Стафф'),
        default=False,
        help_text=_(
            'Аккаунт работника')
    )
    is_active = models.BooleanField(
        _('Активный'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.first_name} {self.patronymic} {self.last_name}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_role(self) -> str:
        if hasattr(self, "professor"):
            return "professor"
        elif hasattr(self, "student"):
            return "student"
        elif self.is_superuser:
            return "admin"
        else:
            return "not set"


class Student(models.Model):
    year_of_enrollment = models.CharField(_('Год поступления'), max_length=4, blank=False)
    record_book_number = models.CharField(_('Номер зачетной книжки'), max_length=20, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='student',
        blank=False, null=False)
    group = models.ForeignKey(
        "CourseGroup",
        on_delete=models.DO_NOTHING,
        related_name='student_group',
        blank=True, null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class Professor(models.Model):
    subjects = models.ManyToManyField("Subject")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='professor',
        blank=False, null=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'


class Direction(models.Model):
    name = models.CharField(_('Название направления'), max_length=50, blank=False)
    subjects = models.ManyToManyField("Subject", related_name="directions")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


class Subject(models.Model):
    name = models.CharField(_('Навзвание предмета'), max_length=150, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


class CourseGroup(models.Model):
    course_number = models.IntegerField(_('Номер курса'), blank=False,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    group_number = models.CharField(_('Номер группы'), max_length=10, blank=False)
    EDUCATION_LEVELS = [
        ('b', "bachelor"),
        ('m', "magistracy"),
        ('p', "postgraduate"),
        ('s', "specialty")
    ]
    EDUCATION_LEVELS_RU = {
        'b': "бакалавриат",
        'm': "магистратура",
        'p': "аспирантура",
        's': "специалитет"
    }
    higher_education_level = models.CharField(
        _('Ступень высшего образования'),
        max_length=1, choices=EDUCATION_LEVELS, blank=True)

    def __str__(self):
        return f"{self.course_number} курс {self.group_number} группа {self.EDUCATION_LEVELS_RU[self.higher_education_level]}"

    class Meta:
        verbose_name = 'Курс-группа'
        verbose_name_plural = 'Курсы-группы'


class GroupMark(models.Model):
    subject = models.ForeignKey("Subject", on_delete=models.DO_NOTHING)
    professor = models.ForeignKey("Professor", on_delete=models.DO_NOTHING)
    group = models.ForeignKey("CourseGroup", on_delete=models.DO_NOTHING)
    semester = models.IntegerField(_("Номер семестра"))

    REPORTING_LEVELS = [
        ('t', "test"),
        ('d', "differentiated test"),
        ('e', "exam")
    ]
    reporting_level = models.CharField(
        _('Отчетность дисциплины'),
        max_length=1, choices=REPORTING_LEVELS, blank=False)

    def __str__(self):
        return f"{self.subject} Профессор: {self.professor} Группа: {self.group} {self.semester} семестр"

    class Meta:
        verbose_name = "Группа оценок"
        verbose_name_plural = 'Группы оценок'


class StudentMark(models.Model):
    mark_group = models.ForeignKey("GroupMark", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.DO_NOTHING)
    att1 = models.IntegerField("Оценка за аттестацию 1", null=True, blank=True)
    att2 = models.IntegerField("Оценка за аттестацию 2", null=True, blank=True)
    att3 = models.IntegerField("Оценка за аттестацию 3", null=True, blank=True)
    exam = models.IntegerField("Оценка за экзамен", null=True, blank=True)
    additional = models.IntegerField("Дополнительные баллы", null=True, blank=True)

    class Meta:
        verbose_name = 'Оценкки студента'
        verbose_name_plural = 'Оценки студентов'

    def __str__(self):
        return f"{self.mark_group} Студента: {self.student}"
