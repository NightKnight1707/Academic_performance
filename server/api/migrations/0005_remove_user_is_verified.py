# Generated by Django 4.2.5 on 2023-09-23 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_course_group_student_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_verified',
        ),
    ]