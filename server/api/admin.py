from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from api.models import User, Student, Professor, Direction, Subject, CourseGroup, StudentMark, GroupMark
from django.utils.translation import gettext_lazy as _

admin.site.unregister(Group)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "patronymic", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "patronymic", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "patronymic", "is_staff")
    search_fields = ("username", "first_name", "last_name", "patronymic", "email")


admin.site.register(User, MyUserAdmin)
admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Direction)
admin.site.register(Subject)
admin.site.register(CourseGroup)
admin.site.register(GroupMark)
admin.site.register(StudentMark)
