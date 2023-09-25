from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from djoser.conf import settings
from djoser.permissions import CurrentUserOrAdmin
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.models import Student, Professor, StudentMark, GroupMark
from api.permissions import IsProfessor
from api.serializers import StudentSerializer, StudentCreateSerializer, ProfessorSerializer, ProfessorCreateSerializer, \
    MyUserSerializer, StudentMarksSerializer, GroupMarkSerializer, SimpleStudentMarksSerializer


class ProfessorViewSet(ModelViewSet):
    serializer_class = ProfessorSerializer
    queryset = Professor.objects.all()
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD
    permission_classes = [IsAdminUser, ]

    def permission_denied(self, request, **kwargs):
        if all((
                settings.HIDE_USERS,
                request.user.is_authenticated,
                self.action in ["update", "partial_update", "list", "retrieve"]
        )):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return ProfessorCreateSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff and user.get_role() == "professor":
            queryset = queryset.filter(pk=user.professor.pk)
        return queryset

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "list"):
            self.permission_classes = [CurrentUserOrAdmin, ]
        return super().get_permissions()


class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD
    permission_classes = [IsAdminUser, ]

    def permission_denied(self, request, **kwargs):
        if all((
                settings.HIDE_USERS,
                request.user.is_authenticated,
                self.action in ["update", "partial_update", "list", "retrieve"]
        )):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        if request.user.get_role() == "student":
            prev_data = {'user': request.data.pop("user", {})}
            request.data.clear()
            request.data.update(prev_data)
        return super().update(request, partial=True)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff and user.get_role() == "student":
            queryset = queryset.filter(pk=user.student.pk)
        return queryset

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "list"):
            self.permission_classes = [CurrentUserOrAdmin, ]
        return super().get_permissions()


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = None
        if user.get_role() == "student":
            s = user.student
            serializer = StudentSerializer(s)
        elif user.get_role() == "professor":
            p = user.professor
            serializer = ProfessorSerializer(p)
        elif user.get_role() == "admin":
            serializer = MyUserSerializer(user)
            serializer = type("TmpUser", (object,), {
                "data": {
                    "id": -1,
                    "user": serializer.data
                }
            })()

        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentMarksView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={
        status.HTTP_200_OK: StudentMarksSerializer(many=True)
    })
    def get(self, request, stud_id, *args, **kwargs):
        try:
            student_marks = StudentMark.objects.filter(student=stud_id).order_by("-mark_group__semester")
        except Student.DoesNotExist:
            student_marks = None

        if not student_marks:
            Response({}, status=status.HTTP_404_NOT_FOUND)

        stud_marks = StudentMarksSerializer(student_marks, many=True)
        return Response(stud_marks.data, status=status.HTTP_200_OK)


class ProfessorMarkGroups(APIView):
    permission_classes = [IsProfessor]

    @extend_schema(request=None, responses={
        status.HTTP_200_OK: GroupMarkSerializer(many=True)
    })
    def get(self, request, *args, **kwargs):
        gms = GroupMark.objects.filter(professor=request.user.professor)
        serializer = GroupMarkSerializer(gms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupMarksView(APIView):
    permission_classes = [IsProfessor]

    @extend_schema(request=None, responses={
        status.HTTP_200_OK: StudentMarksSerializer(many=True)
    })
    def get(self, request, mark_group_id, *args, **kwargs):

        try:
            gm = GroupMark.objects.get(pk=mark_group_id)
        except GroupMark.DoesNotExist:
            gm = None

        if not gm:
            Response({}, status=status.HTTP_404_NOT_FOUND)

        group_students = gm.group.student_group.all()

        sms = []
        for student in group_students:
            res = StudentMark.objects.get_or_create(mark_group=gm, student=student)
            sms.append(res[0])

        serializer = StudentMarksSerializer(sms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=SimpleStudentMarksSerializer,
                   responses={
                       status.HTTP_200_OK: SimpleStudentMarksSerializer(many=True)
                   })
    def put(self, request, mark_group_id, *args, **kwargs):

        try:
            instance = StudentMark.objects.get(pk=mark_group_id)
        except StudentMark.DoesNotExist:
            instance = None

        if not instance:
            Response({}, status=status.HTTP_404_NOT_FOUND)
        instance.att1 = request.data.get("att1")
        instance.att2 = request.data.get("att2")
        instance.att3 = request.data.get("att3")
        instance.additional = request.data.get("additional")
        instance.exam = request.data.get("exam")
        instance.save()

        serializer = StudentMarksSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

