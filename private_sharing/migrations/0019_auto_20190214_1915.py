# Generated by Django 2.1.7 on 2019-02-14 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_sharing', '0018_oauth2datarequestproject_terms_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth2datarequestproject',
            name='deauth_webhook',
            field=models.URLField(blank=True, default='', help_text="The URL to send a POST to when a member\n                     requests data erasure.  This request will be in the form\n                     of JSON,\n                     { 'project_member_id': '12345678', 'erasure_requested': True}", max_length=256, verbose_name='Deauthorization Webhook URL'),
        ),
        migrations.AlterField(
            model_name='oauth2datarequestproject',
            name='terms_url',
            field=models.URLField(help_text='The URL for your "terms of use" (or "terms of service").', verbose_name='Terms of Use URL'),
        ),
    ]
