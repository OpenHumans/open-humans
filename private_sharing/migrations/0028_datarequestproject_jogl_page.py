# Generated by Django 2.2.10 on 2020-07-16 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("private_sharing", "0027_oauth2datarequestproject_webhook_secret")]

    operations = [
        migrations.AddField(
            model_name="datarequestproject",
            name="jogl_page",
            field=models.URLField(
                blank=True, help_text="JOGL project page URL (optional)"
            ),
        )
    ]
