# Generated by Django 5.0.3 on 2024-05-02 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_alter_appointment_date_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='time_schedule',
            field=models.CharField(choices=[('9h - 9h20', '9h - 9h20'), ('9h30 - 9h50', '9h30 - 9h50'), ('10h - 10h20', '10h - 10h20'), ('10h30 - 10h50', '10h30 - 10h50'), ('11h - 11h20', '11h - 11h20'), ('11h30 - 11h50', '11h30 - 11h50'), ('12h - 12h20', '12h - 12h20'), ('14h - 14h20', '14h - 14h20'), ('14h30 - 14h50', '14h30 - 14h50'), ('15h - 15h20', '15h - 15h20'), ('15h30 - 15h50', '15h30 - 15h50'), ('16h - 16h20', '16h - 16h20')], max_length=16),
        ),
    ]