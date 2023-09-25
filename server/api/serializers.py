from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.models import User, Professor, Student, StudentMark, GroupMark, Subject, CourseGroup


class MyUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    patronymic = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    role = serializers.SerializerMethodField('find_role', read_only=True, required=False)

    def find_role(self, obj) -> str:
        return obj.get_role()

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],
                                   first_name=validated_data['first_name'],
                                   last_name=validated_data['last_name'],
                                   patronymic=validated_data['patronymic'],
                                   email=validated_data['email']
                                   )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('pk',
                  'username',
                  'password',
                  'first_name',
                  'last_name',
                  'patronymic',
                  'email',
                  'role',
                  )


class MyUserSerializer(UserSerializer):
    username = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    patronymic = serializers.CharField(max_length=20)
    email = serializers.CharField()
    role = serializers.SerializerMethodField('find_role', read_only=True, required=False)

    def find_role(self, obj) -> str:
        return obj.get_role()

    class Meta:
        model = User
        fields = ('pk',
                  'username',
                  'first_name',
                  'last_name',
                  'patronymic',
                  'email',
                  'role',
                  )
        read_only_fields = (
            'pk',
            'username',
            'email',
        )


class ProfessorCreateSerializer(serializers.ModelSerializer):
    user = MyUserCreateSerializer(required=True)

    class Meta:
        model = Professor
        fields = ('pk', 'user', 'subjects')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = MyUserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        curator = Professor.objects.create(user=user)
        return curator


class StudentCreateSerializer(serializers.ModelSerializer):
    user = MyUserCreateSerializer(required=True)

    class Meta:
        model = Student
        fields = ('pk', 'user', 'year_of_enrollment', 'record_book_number', 'group')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        group = validated_data.pop('group', None)
        user_serializer = MyUserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        student = Student.objects.create(user=user, group=group)
        return student


class WrUserSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        user_obj = instance.user
        user_data = validated_data.pop("user", {})
        instance = super().update(instance, validated_data)
        user_serializer = MyUserSerializer(user_obj, user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        instance.save()
        return instance


class ProfessorSerializer(WrUserSerializer):
    user = MyUserSerializer()

    class Meta:
        model = Professor
        fields = ('pk', 'user', 'subjects')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class CourseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroup
        fields = "__all__"


class StudentSerializer(WrUserSerializer):
    user = MyUserSerializer()
    group = CourseGroupSerializer()

    class Meta:
        model = Student
        fields = ('pk', 'user', 'year_of_enrollment', 'record_book_number', 'group')


class GroupMarkSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    professor = ProfessorSerializer()
    group = CourseGroupSerializer()

    class Meta:
        model = GroupMark
        fields = '__all__'


class StudentMarksSerializer(serializers.ModelSerializer):
    mark_group = GroupMarkSerializer()
    student = StudentSerializer()

    class Meta:
        model = StudentMark
        fields = '__all__'


class SimpleStudentMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMark
        fields = ("id", "att1", "att2", "att3", "additional", "exam",)
