# Generated by Django 5.1.6 on 2025-03-07 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_course_is_free"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="access_type",
        ),
        migrations.RemoveField(
            model_name="course",
            name="discount_price",
        ),
    ]
