# Generated by Django 4.1.6 on 2023-03-03 08:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel_app', '0006_rename_conversation_message_chatroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='read_by',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
