# Generated by Django 4.0.2 on 2023-01-12 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_period_academic_year_alter_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('S', 'Student'), ('I', 'Teacher'), ('A', 'Head Teacher')], default='S', max_length=1, null=True),
        ),
    ]
