# Generated by Django 4.2.5 on 2023-10-05 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_userfollowerlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followrequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester_user_list', to='users.userfollowerlist'),
        ),
        migrations.AlterField(
            model_name='followrequest',
            name='target_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_user_list', to='users.userfollowerlist'),
        ),
    ]
