# Generated by Django 4.0.2 on 2023-03-05 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_instructorshiprequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructorshiprequest',
            name='role',
            field=models.CharField(choices=[('I', 'Teacher'), ('A', 'Head Teacher')], default='I', max_length=1, null=True),
        ),
    ]
