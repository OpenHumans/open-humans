# Generated by Django 2.1.5 on 2019-01-24 00:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('private_sharing', '0013_auto_20190121_2142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datarequestproject',
            name='request_message_permission',
        ),
        migrations.RemoveField(
            model_name='datarequestprojectmember',
            name='message_permission',
        ),
    ]
