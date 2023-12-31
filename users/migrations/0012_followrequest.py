# Generated by Django 4.2.5 on 2023-10-04 23:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_idea_visibility'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester_user', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('requester', 'target_user')},
            },
        ),
    ]
