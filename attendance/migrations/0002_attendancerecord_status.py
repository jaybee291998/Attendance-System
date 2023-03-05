# Generated by Django 4.0.2 on 2023-03-04 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancerecord',
            name='status',
            field=models.CharField(choices=[('P', 'Present'), ('E', 'Excused')], default='P', max_length=1, null=True),
        ),
    ]
