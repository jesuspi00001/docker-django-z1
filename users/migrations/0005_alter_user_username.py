# Generated by Django 4.2.5 on 2023-10-04 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_user_created_at_remove_user_desc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Esta dirección de correo electrónico ya está en uso.'}, max_length=255, unique=True),
        ),
    ]