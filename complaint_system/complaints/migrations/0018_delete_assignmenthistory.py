# Generated by Django 5.2 on 2025-04-18 07:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0017_remove_assignmenthistory_remark_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AssignmentHistory',
        ),
    ]
