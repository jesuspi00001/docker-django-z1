# Generated by Django 4.2.5 on 2023-10-04 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Esta dirección de correo electrónico ya está en uso.'}, max_length=30, unique=True),
        ),
    ]
