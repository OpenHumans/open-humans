# Generated by Django 2.1.7 on 2019-02-22 00:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("private_sharing", "0019_auto_20190214_1915")]

    operations = [
        migrations.RemoveField(
            model_name="datarequestproject", name="request_sources_access"
        ),
        migrations.RemoveField(
            model_name="datarequestprojectmember", name="sources_shared"
        ),
    ]
